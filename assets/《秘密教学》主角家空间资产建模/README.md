# 《秘密教学》主角家空间资产建模

2026-10-14，用户认可 v4 全屋空间。随后明确改用同一模型多机位直接渲染；AI 重绘试制图停止作为正式输出路线。

当前 v4.3 是直接渲染制作样模：客餐厅与四间卧室补充家具、布艺和固定陈设，走廊保留精确木制门牌。卫浴、厨房和辅助区域仍有简化占位家具。全屋精细家具和照片级材质尚未完成，不能把本次样图称为 95 张场景终稿。

- `模型/秘密教学_全屋空间_v4.blend`：已认可中性基线。
- `模型/秘密教学_主角家_v4.1.blend`：制作模型；三扇卧室门关闭，文字已转网格，品牌图片已内嵌。
- `模型/秘密教学_主角家_直接渲染_v4.3.blend`：最新直接渲染样模，原模型仍作为已认可结构基线。
- `模型/空间主数据_v4.json`：结构唯一依据；`空间制作配置_v4.1.json`：灯光、机位、门牌。
- `打开检查模型.html`：离线查看已认可结构，仍为 v4 中性视图；制作新增标牌见 v4.1 Blender/GLB。
- `制作记录/制作清单.json`：95 正式场景 + 2 辅助关系图。只有有文件与实际检查证据的条目才可标记合格。

## 生成与校验

要求 Blender 4.5、Python 3.10+。依赖从项目目录定位；系统工具位置由调用者配置。先执行 `git lfs pull`。

在本资产目录运行下列命令。直接拍摄已有模型使用 `render_saved.py`，它只切换真实摄影机和灯光，不重新建模，也不调用 AI：

```powershell
blender -b --disable-autoexec --python scripts/render_saved.py -- --list
blender -b --disable-autoexec --python scripts/render_saved.py -- --camera "DIRECT_客厅_后视图" --time both
```

默认输出到 `预览/保存模型拍摄/`。需要修改家具后重建模型时，才使用下面的制作命令：

```powershell
python scripts/check_and_draw.py
blender -b --python scripts/verify_blend.py
blender -b --python scripts/production_blender.py -- --font "你的可用中文字体.ttf"
python scripts/fetch_cc0.py
blender -b --python scripts/direct_render.py -- --samples 80
blender -b --python scripts/check_direct_model.py
python scripts/package_direct_review.py
```

`prepare_production.py` 用于首次初始化，不能在已有生成状态后直接运行覆盖制作清单。CJK 字体必须含中文及「の」；仅转换后的字符网格进入模型，不打包操作系统字体。打开已保存 v4.3 模型和运行直接渲染脚本不需要该字体。

## 画面规则

白天使用天空散射光；夜晚为明亮柔和暖白主光，淡黄局部灯光。二姐蓝紫光仅作局部点缀。原家具和床品身份保持；固定物件换机位不移动。姓名牌为「舒亚の窝」「子豪の窝」「薇亚的窝」。每个空间仅一个固定黄瓜短剧标牌，无域名。

正式图不得让门框、门楣或房梁占据镜头前景。俯拍从房间内部高位取景；检查用剖切必须单独标注，不能充当自然机位。正面三门关系图采用标明的正交剖切，仅作关系参考。

植物使用 Poly Haven 的两个 CC0 模型，来源、文件校验值和许可链接保存在 `资源/PolyHaven/来源与许可.json`。保存的 v4.3 Blender 模型内嵌使用到的纹理，直接打开渲染不依赖下载脚本。`detail_rooms.py` 的家具是按参考手工参数建模，尚未完整复刻原图细节；没有使用 AI 重绘补画。

## 保存边界

模型、必要参考、品牌和图纸以 LFS 保存；代码、清单、提示词和检查结果以 Git 保存。最终场景图和漫游保存在本地场景全集，仓库只记录相对文件名、状态与 SHA-256。原始用户素材不删除；旧生成图仅在对应替代图通过检查后移出最新目录。

已推送私有仓库专用分支 `codex/20261014-secret-teaching-home-assets`，没有修改 main。通过独立 HTTPS 克隆及 LFS 下载验证：42 个文件路径、38 个独立 LFS 对象校验一致；恢复后的模型能打开、离线预览能用，并能直接渲染。详细证据见 `制作记录/远端恢复校验.json`。额度接口在当前授权下不可读取，但本次实际上传和下载已成功。
