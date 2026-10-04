"""Behavioral regression tests; approval text here is synthetic fixture evidence."""
import base64
import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
import project_state_v2 as v
from migrate_project_state import migrate_file, migrate

PNG = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII=')


class StateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        (self.base / 'image.png').write_bytes(PNG)

    def image(self, artifact):
        artifact['media'] = dict(path='image.png', sha256=hashlib.sha256(PNG).hexdigest(),
                                 reviewed=True, reviewed_version=artifact['version'], review_note='Synthetic fixture image')

    def confirm(self, state, stage):
        return v.approve_pending_gate(v.submit_review(state, stage, self.base), 'Fixture user confirms these exact results', self.base)

    def production(self, board_style='black_white_lineart'):
        s = v.new_state('TEST', aspect='16:9')
        for suffix in ('A', 'B'):
            a = v.new_artifact('SC-' + suffix, 'scene', dict(heading='01－01｜修理铺｜日｜内', text='女孩接过修好的表。'))
            a['status'] = 'ready'
            s['artifacts'].append(a)
        s = self.confirm(s, 'script')
        for suffix in ('A', 'B'):
            a = v.new_artifact('SH-' + suffix, 'shot', dict(size='中景', camera='平视固定', action='接表', sound='谢谢。', join='直切'),
                               [v.dependency(v.index(s)['SC-' + suffix])])
            a['status'] = 'ready'
            s['artifacts'].append(a)
        s = self.confirm(s, 'shot_plan')
        # One shared character plus an independent object demonstrates reuse and fan-out.
        for aid, users in [('CHAR', ['SH-A', 'SH-B']), ('PROP', ['SH-B'])]:
            a = v.new_artifact(aid, 'asset', dict(role='character' if aid == 'CHAR' else 'prop', description='已有合格素材', used_by=users),
                               [v.dependency(v.index(s)['SC-B'], ('visual',))])
            self.image(a)
            a['status'] = 'ready'
            s['artifacts'].append(a)
        s = self.confirm(s, 'assets')
        for suffix in ('A', 'B'):
            deps = [v.dependency(v.index(s)['SH-' + suffix], ('visual', 'performance')), v.dependency(v.index(s)['CHAR'], ('visual',))]
            if suffix == 'B':
                deps.append(v.dependency(v.index(s)['PROP'], ('visual',)))
            a = v.new_artifact('BOARD-' + suffix, 'board', dict(style=board_style, panel_aspect='16:9', row_lengths=[1],
                               panels=[dict(id='P-' + suffix, shot_id='SH-' + suffix, state='表已在女孩手中')]), deps)
            self.image(a)
            a['status'] = 'ready'
            s['artifacts'].append(a)
        s = self.confirm(s, 'storyboard')
        s['model_profiles'] = [dict(id='TEST-ENTRY', model='fixture-model', entry='test-only', verified_at='2026-10-03', source='fixture spec, not a product claim',
                                   supports_combined_refs=True, limits=dict(duration_seconds=12, images=3, prompt_characters=1000))]
        for suffix in ('A', 'B'):
            unit = v.new_artifact('UNIT-' + suffix, 'unit', dict(duration_seconds=7, start_state='伸手', end_state='接表', join='直切'),
                                  [v.dependency(v.index(s)['SH-' + suffix]), v.dependency(v.index(s)['BOARD-' + suffix])])
            unit['status'] = 'ready'
            s['artifacts'].append(unit)
            prompt = v.new_artifact('PROMPT-' + suffix, 'prompt', dict(text='女孩接过手表：“谢谢。”', profile_id='TEST-ENTRY', references=[
                dict(id='CHAR', name='@图片1', role='identity_appearance_space'),
                dict(id='BOARD-' + suffix, name='@图片2', role='composition_action')]),
                [v.dependency(unit), v.dependency(v.index(s)['CHAR'], ('visual',)), v.dependency(v.index(s)['BOARD-' + suffix])])
            prompt['status'] = 'ready'
            s['artifacts'].append(prompt)
        s['delivery']['status'] = 'ready'
        self.assertEqual([], v.validate(s)[0])
        return s

    def test_four_confirmations_and_direct_compilation(self):
        s = self.production()
        self.assertEqual(4, len(s['approvals']))
        self.assertEqual('compile', s['stage'])
        self.assertEqual([], v.verify_media(s, self.base))
        with self.assertRaises(ValueError):
            v.submit_review(s, 'compile', self.base)

    def test_unselected_aspect_allows_script_but_blocks_ready_shot(self):
        s = v.new_state('UNDECIDED')
        self.assertIsNone(s['format'])
        scene = v.new_artifact('SC', 'scene', dict(heading='1－1｜店内｜日｜内', text='店主递出手表。'))
        scene['status'] = 'ready'
        s['artifacts'].append(scene)
        s = self.confirm(s, 'script')
        shot = v.new_artifact('SH', 'shot', dict(size='中景', camera='固定', action='递表', sound='谢谢', join='切'),
                              [v.dependency(v.index(s)['SC'])])
        shot['status'] = 'ready'
        s['artifacts'].append(shot)
        with self.assertRaisesRegex(ValueError, 'aspect must be selected'):
            v.submit_review(s, 'shot_plan', self.base)
        s['format'] = '9:16'
        self.assertEqual('shot_plan', self.confirm(s, 'shot_plan')['approvals'][-1]['stage'])

    def test_logged_spatial_failure_blocks_board_review(self):
        s = v.apply_change(self.production(), ['BOARD-A'], 'visual', 'Wrong doorway and actor positions')
        board = v.index(s)['BOARD-A']
        board['content']['blocking_issues'] = ['Door replaces a window']
        self.image(board)
        board['status'] = 'ready'
        with self.assertRaisesRegex(ValueError, 'unresolved storyboard'):
            v.submit_review(s, 'storyboard', self.base)

    def test_color_board_uses_same_four_gates_and_reference_roles(self):
        s = self.production('color')
        self.assertEqual(4, len(s['approvals']))
        self.assertEqual('compile', s['stage'])
        self.assertEqual([], v.verify_media(s, self.base))
        self.assertEqual('composition_action', v.index(s)['PROMPT-A']['content']['references'][1]['role'])

    def test_style_change_only_invalidates_board_and_its_downstream(self):
        original = self.production()
        s = v.apply_change(original, ['BOARD-A'], 'visual', 'User chooses color for this board')
        self.assertEqual({'BOARD-A', 'UNIT-A', 'PROMPT-A'}, set(s['change_log'][-1]['affected']))
        for aid in ('SC-A', 'SH-A', 'CHAR', 'BOARD-B', 'PROMPT-B'):
            self.assertEqual(v.index(original)[aid], v.index(s)[aid])
        board = v.index(s)['BOARD-A']
        board['content']['style'] = 'color'
        self.assertIsNone(board['approved_version'])
        self.image(board)
        board['status'] = 'ready'
        s['delivery']['status'] = 'draft'
        s = v.submit_review(s, 'storyboard', self.base)
        self.assertEqual(['BOARD-A'], [r['id'] for r in s['pending_review']['items']])
        s = v.approve_pending_gate(s, 'Fixture confirms revised color image', self.base)
        self.assertEqual('approved', v.index(s)['BOARD-A']['status'])
        self.assertEqual('stale', v.index(s)['PROMPT-A']['status'])

    def test_unknown_board_style_and_silent_style_edit_rejected(self):
        s = self.production('color')
        v.index(s)['BOARD-A']['content']['style'] = 'sepia_unknown'
        self.assertTrue(any('board requires' in e for e in v.validate(s)[0]))
        s = self.production()
        v.index(s)['BOARD-A']['content']['style'] = 'color'
        self.assertTrue(any('approval does not bind' in e for e in v.validate(s)[0]))

    def test_dialogue_change_preserves_other_scene_and_shared_appearance(self):
        s = self.production()
        changed = v.apply_change(s, ['SC-A'], 'dialogue', '更自然的对白')
        affected = set(changed['change_log'][-1]['affected'])
        self.assertEqual({'SC-A', 'SH-A', 'BOARD-A', 'UNIT-A', 'PROMPT-A'}, affected)
        for aid in ('SC-B', 'SH-B', 'CHAR', 'PROP', 'BOARD-B', 'UNIT-B', 'PROMPT-B'):
            self.assertEqual(v.index(s)[aid], v.index(changed)[aid])
        self.assertEqual([], v.validate(changed)[0])
        self.assertEqual('approved', v.index(s)['SC-A']['status'])

    def test_shared_character_reaches_every_usage(self):
        changed = v.apply_change(self.production(), ['CHAR'], 'visual', '服装变更')
        self.assertEqual({'CHAR', 'SH-A', 'SH-B', 'BOARD-A', 'BOARD-B', 'UNIT-A', 'UNIT-B', 'PROMPT-A', 'PROMPT-B'},
                         set(changed['change_log'][-1]['affected']))
        self.assertEqual('approved', v.index(changed)['PROP']['status'])
        self.assertEqual([], v.validate(changed)[0])

    def test_wording_only_and_global_revision(self):
        s = self.production()
        s['revision'] += 100
        self.assertEqual([], v.validate(s)[0])
        changed = v.apply_change(s, ['PROMPT-A'], 'wording', '删除重复修饰')
        self.assertEqual(['PROMPT-A'], changed['change_log'][-1]['affected'])
        with self.assertRaises(ValueError):
            v.apply_change(s, ['SC-A'], 'wording', '绕过审批')

    def test_no_in_place_approval_or_review_tampering(self):
        s = self.production()
        v.index(s)['SC-A']['content']['text'] = '换了整个结局'
        self.assertTrue(any('approval does not bind' in e for e in v.validate(s)[0]))
        s = v.new_state()
        scene = v.new_artifact('SC', 'scene', dict(heading='1－1｜屋内｜日｜内', text='关门。'))
        scene['status'] = 'ready'
        s['artifacts'].append(scene)
        s = v.submit_review(s, 'script')
        s['artifacts'][0]['content']['text'] = '开门。'
        with self.assertRaises(ValueError):
            v.approve_pending_gate(s, '同意')

    def test_image_tool_failure_is_not_completion(self):
        s = self.production()
        asset = v.index(s)['CHAR']
        asset.pop('media')
        asset['content']['prompt'] = '生成一个人'
        self.assertTrue(any('actual, visually reviewed image' in e for e in v.validate(s)[0]))
        s = self.production()
        (self.base / 'image.png').write_bytes(b'changed')
        self.assertTrue(v.verify_media(s, self.base))

    def test_reference_responsibilities_and_missing_alias(self):
        s = self.production()
        p = v.index(s)['PROMPT-A']['content']
        p['references'][1]['role'] = 'identity_appearance_space'
        p['text'] += ' @图片9'
        errors = v.validate(s)[0]
        self.assertTrue(any('responsibility' in e for e in errors))
        self.assertTrue(any('fabricated' in e for e in errors))

    def test_one_odd_many_panels_and_pages(self):
        for rows in ([1], [3, 2], [4, 4, 3]):
            with self.subTest(rows=rows):
                s = self.production()
                s = v.apply_change(s, ['BOARD-A'], 'visual', '变更布局')
                s = v.refresh_dependencies(s, 'BOARD-A')
                b = v.index(s)['BOARD-A']
                b['content']['row_lengths'] = rows
                b['content']['panels'] = [dict(id=f'PA-{i}', shot_id='SH-A', state=f'状态{i}') for i in range(sum(rows))]
                self.image(b)
                b['status'] = 'ready'
                self.assertEqual([], v.validate(s)[0])
                b['content']['row_lengths'] = [sum(rows) + 1]
                self.assertTrue(any('layout' in e for e in v.validate(s)[0]))

    def test_stale_dependency_cannot_be_marked_ready(self):
        s = v.apply_change(self.production(), ['SC-A'], 'dialogue', '新对白')
        v.index(s)['SH-A']['status'] = 'ready'
        self.assertTrue(any('stale dependency' in e for e in v.validate(s)[0]))

    def test_refresh_does_not_approve(self):
        s = v.apply_change(self.production(), ['PROMPT-A'], 'wording', '删重复')
        s = v.refresh_dependencies(s, 'PROMPT-A')
        self.assertEqual('draft', v.index(s)['PROMPT-A']['status'])
        self.assertIsNone(v.index(s)['PROMPT-A']['approved_version'])

    def test_cycles_unknown_ids_and_invalid_shapes(self):
        s = self.production()
        v.index(s)['SC-A']['depends_on'] = [v.dependency(v.index(s)['SH-A'])]
        self.assertTrue(any('cycle' in e for e in v.validate(s)[0]))
        for mutation in [lambda s: s.update(artifacts={}), lambda s: s['artifacts'][0].update(depends_on=[{}]),
                         lambda s: s['artifacts'][0].update(aspect_versions=[]), lambda s: s.update(approvals=[None])]:
            s = self.production()
            mutation(s)
            self.assertTrue(v.validate(s)[0])

    def test_limits_and_missing_shot_coverage(self):
        s = self.production()
        s['model_profiles'][0]['limits']['duration_seconds'] = 5
        self.assertTrue(any('duration limit' in e for e in v.validate(s)[0]))
        s = self.production()
        s['artifacts'] = [a for a in s['artifacts'] if a['id'] not in ('UNIT-B', 'PROMPT-B')]
        self.assertTrue(any('missing from compilation' in e for e in v.validate(s)[0]))

    def test_unrelated_change_preserves_pending_review(self):
        s = v.apply_change(self.production(), ['BOARD-A'], 'visual', '局部画板修复')
        s = v.refresh_dependencies(s, 'BOARD-A')
        board = v.index(s)['BOARD-A']
        self.image(board)
        board['status'] = 'ready'
        s = v.submit_review(s, 'storyboard', self.base)
        changed = v.apply_change(s, ['PROMPT-B'], 'wording', '独立单元措辞')
        self.assertEqual(s['pending_review'], changed['pending_review'])
        self.assertEqual('storyboard', changed['stage'])
        self.assertEqual([], v.validate(changed)[0])

    def test_rendered_change_propagates_as_visual_fact(self):
        s = self.production()
        changed = v.apply_change(s, ['SH-A'], 'dialogue', '引起表演反应改变')
        self.assertEqual(2, v.index(changed)['BOARD-A']['aspect_versions']['visual'])

    def test_unsupported_reference_mode_and_text_disguised_as_image(self):
        s = self.production()
        s['model_profiles'][0]['supports_combined_refs'] = False
        self.assertTrue(any('unsupported or unverified' in e for e in v.validate(s)[0]))
        fake = b'text prompt instead of image'
        (self.base / 'image.png').write_bytes(fake)
        for a in s['artifacts']:
            if 'media' in a:
                a['media']['sha256'] = hashlib.sha256(fake).hexdigest()
        self.assertTrue(any('image signature' in e for e in v.verify_media(s, self.base)))

    def test_entry_blocker_prevents_ready_prompt(self):
        s = self.production()
        s['model_profiles'][0]['blockers'] = ['Reference acceptance not yet checked']
        self.assertTrue(any('unresolved blockers' in e for e in v.validate(s)[0]))

    def test_populated_legacy_ids_and_media_survive(self):
        from test_validate_project_state import sequence_state
        original = sequence_state(['normal', 'normal'])
        original['approval_gates']['shot_breakdown'].update(status='approved', approved_revision=1)
        original['assets'] = [dict(id='BOARD-OLD', status='draft', path='media/old.png', style='color_render')]
        original['segments'][0]['storyboard_asset_ids'] = ['BOARD-OLD']
        migrated = migrate(original)
        self.assertEqual(original, migrated['legacy_snapshot'])
        self.assertIn('SEG-01', v.index(migrated))
        self.assertEqual('color_render', v.index(migrated)['BOARD-OLD']['content']['style'])
        self.assertEqual('media/old.png', v.index(migrated)['BOARD-OLD']['content']['legacy_data']['path'])
        self.assertEqual([], migrated['approvals'])
        self.assertEqual([], v.validate(migrated)[0])

    def test_migration_no_overwrite_loss_or_approval_fabrication(self):
        original = json.loads((Path(__file__).parent / 'fixtures/project-state-1.9.json').read_text(encoding='utf-8'))
        original['custom_notes'] = {'preserve': ['unknown field', 'old approval evidence']}
        source, target = self.base / 'old.json', self.base / 'new.json'
        source.write_text(json.dumps(original), encoding='utf-8')
        before = source.read_bytes()
        migrated = migrate_file(source, target)
        self.assertEqual(before, source.read_bytes())
        self.assertEqual(original, migrated['legacy_snapshot'])
        self.assertEqual([], migrated['approvals'])
        self.assertEqual([], v.validate(migrated)[0])
        for destination in (source, target):
            with self.assertRaises(ValueError):
                migrate_file(source, destination)
        with self.assertRaises(ValueError):
            migrate(v.new_state())


if __name__ == '__main__':
    unittest.main()
