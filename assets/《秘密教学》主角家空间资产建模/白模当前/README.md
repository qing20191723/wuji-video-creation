# P2.4-M2 当前白模

[打开可旋转白模](查看白模.html?rev=P2.4-M2&cam=F4_DOWN) · [12个渲染视角与原图对照](F4建模对照.html) · [已确认F4关系](../平面确认/打开平面图.html)

用户确认F4关系，并授权调整二楼房间宽深比例。当前Blender、GLB、查看器、两张建模平面与渲染来自同一份`模型/建模方案.json`。模型版本P2.4-M2，尚未获用户对三维成品的确认。

- 三卧室门序、平行直梯、C二楼端部地面、B一楼下平台、A大窗前上平台按F4重建。撤除R2的额外挑空和辅助房门。
- 层高3.30m，板厚0.22m；22级高差0.15m，21踏面0.36m，实际梯段及侧护栏7.56m。所有数值为暂定实现，用户仍可校准。
- 二楼卧室净宽3.20/3.30/3.90m，净深5.80m；大姐床保持2.25×2.10m。家具重新布置，详细前后占地见建模方案的`furniture_changes`。
- 一楼主要功能、家具、花园及车库保持；楼梯下口接到客厅东侧通路。二楼缩窄后西侧保留屋面露台，外立面与原图尺寸尚需后续核对。
- 二楼公卫、布草无已确认位置，本版未补造房间。全空间无盲角覆盖、柜门抽屉状态、独立1080p漫游视频未完成。

## 检查

771个模型网格已由Blender回读核对，GLB导入771个网格；玻璃透明模式正确。17项局部几何与动线检查通过，指定路线724个采样点有连续支承，0.50m足迹无列检障碍，最小楼板/屋顶净空3.08m。检查范围不等于结构施工验收或全空间覆盖验收。

查看器提供完整模型、楼层隐藏、机位跳转、门扇开启、截图及正反向连续路线。静态图可直接批注。渲染图保存在本地，仓库保存源数据和文件校验清单。

## 再生成

使用Blender运行 `scripts/build_p23.py -- --f4 --render --cameras F4_DOWN,F4_REVERSE,F4_C,F4_UP,F4_STAIR_DOWN,F4_B_CONNECT,F4_PLAN,B1_01,B1_TOP,B2_TOP,B3_TOP,EXT_01`；前置运行`prepare_f4_model.py`，后续运行`audit_f4_model.py`、`verify_m2_blend.py`（Blender）、`package_m2.py`和`check_m2.cjs`。依赖本地Blender、Python/Pillow与Node/Playwright。

## 数据字段范围

`rooms/furniture/walls/openings/stairs/architecture/exterior_rails`是本版建模依据，`walk_route`是本版连续检查路线。继承的`clearances/routes/reference_relationships`仅保留旧方案记录，未作为本版空间验收或当前路线依据；当前检查结论以`检查记录/M2几何与动线检查.json`为准。
