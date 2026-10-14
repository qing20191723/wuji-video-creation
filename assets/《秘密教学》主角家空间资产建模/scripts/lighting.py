"""One shared day/night preset for building and rendering the saved model."""
def set_time(scene,objects,night):
    bg=scene.world.node_tree.nodes['Background']
    bg.inputs[0].default_value=(.12,.18,.32,1) if night else (.84,.89,1,1)
    bg.inputs[1].default_value=.045 if night else .65
    for o in objects:
        if o.type!='LIGHT':continue
        inside='检查光' in o.name
        o.data.energy=max(25,min(370,o.get('room_area',20)*(9 if night else 4))) if inside else (20 if night else 3800)
        o.data.color=(1,.94,.84) if night and inside else (1,1,1)
    scene['time_state']='night' if night else 'day'
    scene.view_settings.exposure=.15
