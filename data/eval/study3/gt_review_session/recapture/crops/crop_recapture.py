# Recapture review crops: opendtect__horizon_2dviewer__01 s6-s8 (2026-09-23)
# usage: python crop_recapture.py   (run from gt_review_session/)
from PIL import Image
SC = 'opendtect__horizon_2dviewer__01'
CROPS = [
    # step 6 (1920x1032)
    (6, 'top',          (0, 0, 960, 110), 3),
    (6, 'tree_main',    (45, 115, 305, 400), 3),
    (6, 'settings',     (70, 380, 710, 745), 3),
    (6, 'viewer_head',  (715, 245, 1712, 310), 3),
    (6, 'viewer_tree',  (745, 310, 1010, 480), 3),
    (6, 'output_dlg',   (735, 530, 1270, 670), 3),
    (6, 'plot_top',     (1010, 310, 1712, 380), 3),
    (6, 'plot_left',    (1010, 350, 1090, 720), 3),
    (6, 'plot_ms',      (1012, 470, 1045, 535), 8),
    (6, 'plot_right',   (1630, 350, 1712, 720), 3),
    (6, 'plot_bottom',  (1010, 690, 1712, 760), 3),
    (6, 'axes_l',       (420, 175, 1100, 255), 3),
    (6, 'axes_r',       (1000, 175, 1720, 255), 3),
    (6, 'scene200',     (520, 220, 600, 255), 8),
    (6, 'scene_bl',     (430, 750, 560, 800), 4),
    (6, 'nez',          (1790, 915, 1900, 1005), 3),
    (6, 'status_l',     (0, 1008, 960, 1032), 3),
    (6, 'status_r',     (960, 1008, 1920, 1032), 3),
    # step 7 (1922x1041)
    (7, 'top',          (0, 0, 960, 120), 3),
    (7, 'tree_main',    (45, 125, 305, 590), 3),
    (7, 'viewer_head',  (615, 330, 1612, 395), 3),
    (7, 'viewer_tree',  (650, 395, 910, 560), 3),
    (7, 'plot_top',     (910, 395, 1612, 445), 3),
    (7, 'plot_left',    (910, 430, 1000, 820), 3),
    (7, 'plot_right',   (1530, 430, 1612, 810), 3),
    (7, 'plot_bottom',  (910, 790, 1612, 840), 3),
    (7, 'axes_l',       (420, 185, 1100, 262), 3),
    (7, 'axes_r',       (1000, 185, 1720, 262), 3),
    (7, 'scene200',     (520, 228, 600, 262), 8),
    (7, 'scene_labels', (430, 380, 540, 610), 3),
    (7, 'scene_bl',     (430, 760, 560, 810), 4),
    (7, 'nez',          (1790, 925, 1900, 1015), 3),
    (7, 'status_l',     (0, 1018, 640, 1041), 3),
    (7, 'status_m',     (640, 1018, 1280, 1041), 3),
    (7, 'status_r',     (1280, 1018, 1922, 1041), 3),
    # step 8 (1922x1041)
    (8, 'top',          (0, 0, 960, 120), 3),
    (8, 'tree_main',    (45, 125, 305, 590), 3),
    (8, 'axes_l',       (420, 185, 1100, 262), 3),
    (8, 'axes_r',       (1000, 185, 1720, 262), 3),
    (8, 'scene200',     (520, 228, 600, 262), 8),
    (8, 'scene_labels', (430, 380, 540, 610), 3),
    (8, 'scene_bl',     (430, 760, 560, 810), 4),
    (8, 'picks',        (690, 755, 980, 835), 3),
    (8, 'nez',          (1790, 925, 1900, 1015), 3),
    (8, 'status_l',     (0, 1018, 960, 1041), 3),
    (8, 'status_r',     (960, 1018, 1922, 1041), 3),
]
for step, name, box, scale in CROPS:
    im = Image.open(f'screenshots/{SC}/step_{step}.jpg')
    c = im.crop(box)
    c = c.resize((c.width * scale, c.height * scale), Image.LANCZOS)
    out = f'recapture/crops/{SC}__s{step}__{name}.png'
    c.save(out)
    print(out, c.size)
