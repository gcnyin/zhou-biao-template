# -*- coding: utf-8 -*-
"""从 demo 原图提取模板素材（C 背景 + 贴纸裁片、A 头图 + 头像裁片）。
用法：python3 tools/extract_assets.py  （需 pillow + numpy：pip install pillow numpy）
"""
from PIL import Image, ImageFilter
import numpy as np
import os

D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'demo')

# ---------- 模板 C：原图做背景，擦掉手写文字（保留全部装饰） ----------
im = Image.open(f'{D}/jjj-9-sep-wk4.png').convert('RGB')
a = np.asarray(im).astype(int)
r, g, b = a[..., 0], a[..., 1], a[..., 2]
text = (r - g > 22) & (r - b > 22)
tmask = Image.fromarray((text * 255).astype('uint8')).filter(ImageFilter.MaxFilter(7))
text = np.asarray(tmask) > 0

regions = [
    (262, 240, 715, 336),    # -击剑剑本周-
    (180, 328, 808, 480),    # -Schedule-
    (130, 538, 288, 1258),   # 星期列
    (296, 538, 558, 1258),   # 时间列
    (570, 512, 940, 1128),   # 内容列
    (293, 1272, 686, 1434),  # “作业太多惹”双线框整体（HTML 原位重建）
]
out = a.copy()
for (x0, y0, x1, y1) in regions:
    sub = out[y0:y1, x0:x1]
    sub_t = text[y0:y1, x0:x1]
    med_region = np.median(sub[~sub_t], axis=0) if (~sub_t).any() else np.median(sub, axis=(0, 1))
    for i in range(sub.shape[0]):
        row, rt = sub[i], sub_t[i]
        if rt.any() and (~rt).any():
            row[rt] = np.median(row[~rt], axis=0)
        elif rt.all():
            row[rt] = med_region

res = Image.fromarray(out.astype('uint8'))
res.save(f'{D}/c-bg.jpg', quality=90)
res.crop((766, 96, 1034, 364)).save(f'{D}/c-ava.jpg', quality=92)
res.crop((18, 1268, 292, 1518)).save(f'{D}/c-sti-l.jpg', quality=92)
res.crop((690, 1180, 1080, 1527)).save(f'{D}/c-sti-r.jpg', quality=92)

# ---------- 模板 A：头图 + 5 个 chibi 头像（不含名字文字） ----------
ima = Image.open(f'{D}/2607A1B6998FF92258FAE1C203F62A51.png').convert('RGB')
ima.crop((12, 12, 988, 558)).save(f'{D}/a-banner.jpg', quality=90)
crops = [(46,795,144,874), (46,898,144,976), (46,1005,144,1082), (46,1176,144,1266), (46,1298,144,1362)]
for i, box in enumerate(crops):
    ima.crop(box).save(f'{D}/a-ava{i}.jpg', quality=92)
print('assets extracted to', D)
