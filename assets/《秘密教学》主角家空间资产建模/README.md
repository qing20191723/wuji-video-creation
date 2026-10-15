# 《秘密教学》主角家空间资产建模

当前工作为 **v5 原图校准与采光院拼接提案**。用户选择优先保留 V3 卧室，允许走廊转折或增加采光院；正式场景图片暂停，等模型复核后恢复。下方 v4.4 内容保留作历史记录，不是当前生产基线。

- [打开 V5 可旋转模型](打开V5校准模型.html)：单文件离线预览，支持一楼、二楼、楼梯及独立房间检查。
- [V5 两层同向平面图](图纸/全屋两层同向平面_v5.svg)：同一数据生成的可编辑 SVG；旁有 PNG 与门窗编号 CSV。
- [模型与复核说明](制作记录/V5采光院拼接与复核说明.md)：原图依据、尺寸、补充设计、局限及下次验收重点。
- `模型/秘密教学_V3校准模块_v5.blend`、同名 GLB：8 个分组（6 个房间模块、旧外部体量研究、全屋提案），各模块沿 X 轴分隔存放；HOME 是新全屋，SITE 仅用于对照。
- `模型/空间校准主数据_v5.json`：所有几何和机位的唯一坐标来源。
- `预览/v5/对照与复核.html`：本地原图对照，预览目录不进 Git，可用原素材重建。

在本资产目录构建 v5：

```powershell
python scripts/build_v5_modules.py
python scripts/check_v5.py
python scripts/check_v5_access.py
python scripts/plan_v5.py
blender -b --disable-autoexec --python scripts/export_v5_blender.py
blender -b --disable-autoexec --python scripts/check_saved_v5.py
python scripts/package_v5.py --reference-root "你的场景图V3版目录"
node scripts/verify_v5.cjs
```

检查依赖 NumPy、Playwright 和 Chrome；`NODE_PATH` / `CHROME_PATH` 按环境配置。浏览器验证同时输出 PNG 图纸。模型保持实际墙高，去顶图仅供检查。42 张必要 V3 参考按校验值保存于 `参照/V3/`，`package_v5.py` 不传参数时使用它们；本地渲染需重新运行 Blender 导出脚本。单文件模型预览和 Blend 打开不依赖原图路径。

## 历史：v4.4 路线

2026-10-14，用户认可 v4 基本空间后，进一步明确：模型作为空间参考，先确定摄影机，再由 imagegen 结合原场景修正材质。当前工作版为 v4.4，旧直接渲染流程作为历史保留。

v4.4 修复预览默认截矮墙体及视场换算，增加 H203 后露台方向高位摄影机，将走廊唯一 Logo 固定到护栏端墙。首张材质修正版仍为待核对样图：远端两块门牌不能逐字验清，生成边线也不是逐像素锁定。房间比例、辅助区效率尚未完成校准；95 张场景终稿不能据此宣称完成。

- `模型/秘密教学_主角家_v4.4.blend`：当前打包材质模型，保留全高墙体与 H203 摄影机。
- `模型/秘密教学_空间结构_v4.4.glb`：轻量结构导出；不含全部精细材质。
- `模型/空间主数据_v4.4.json`：当前空间、机位与 Logo 位置；原 v4 为认可基线。
- `v4.4首张对照检查.html`：本地样图与底图对照（图片不进 Git，恢复仓库后需从本地场景集取回）。
- `校验/空间复核_v4.4.md`：已修正项、尺寸保留依据与未解决问题。

历史模型：

- `模型/秘密教学_全屋空间_v4.blend`：已认可中性基线。
- `模型/秘密教学_主角家_v4.1.blend`：制作模型；三扇卧室门关闭，文字已转网格，品牌图片已内嵌。
- `模型/秘密教学_主角家_直接渲染_v4.3.blend`：上一版直接渲染样模，作为 v4.4 构建输入保留。
- `模型/空间主数据_v4.json`、`空间制作配置_v4.1.json`：历史基线与制作配置。
- `打开检查模型.html`：离线查看 v4.4，默认完整墙高；真实机位三门关闭，漫游/平面模式开门。姓名文字与完整材质以 Blender 为准。
- `制作记录/制作清单.json`：95 正式场景 + 2 辅助关系图。只有有文件与实际检查证据的条目才可标记合格。

## 生成与校验

要求 Blender 4.5、Python 3.10+。依赖从项目目录定位；系统工具位置由调用者配置。先执行 `git lfs pull`。

当前版的可复现入口：

```powershell
blender -b --disable-autoexec --python scripts/build_v44.py
python scripts/check_v44.py
blender -b --disable-autoexec --python scripts/check_saved_v44.py
blender -b --disable-autoexec --python scripts/project_openings_v44.py
python scripts/diagnostics_v44.py
python scripts/package_review.py
```

`revise_v44.py` 仅为一次性迁移脚本，当前 v4.4 已存在时拒绝执行，避免重置制作状态。生图使用内置 imagegen，实际提示词和参考校验值见 `制作记录/H203_制作与检查_v4.4.json`。模型检查所需 NumPy、图像元数据读取所需 Pillow 和浏览器检查所需 Playwright 由运行环境提供；不将本机工具绝对路径作为项目依赖。

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

私有仓库专用分支为 `codex/20261014-secret-teaching-home-assets`，不修改 main。旧版远端恢复证据见 `制作记录/远端恢复校验.json`；v4.4 的备份状态以另存的 v4.4 验证记录为准，不能沿用旧版成功结果。

v4.4 已完成独立 HTTPS 克隆及新增 LFS 文件恢复验证：模型、GLB、图纸 PNG 的 SHA-256 一致，保存模型可打开且贴图已内嵌，离线预览通过。证据见 `制作记录/远端恢复校验_v4.4.json`。此结论只涵盖备份，不代表样图或全屋尺寸已验收。
