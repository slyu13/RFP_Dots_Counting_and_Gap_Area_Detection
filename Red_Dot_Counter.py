import cv2
import numpy as np
import os
import glob
import pandas as pd
import openpyxl
from datetime import datetime

# 单张图像检测函数
def count_red_spots_with_contrast(
        input_image_path: str,
        output_image_path: str,
        min_distance_between_spots: float = 8.0,
        ambient_scale: float = 2.0,
        contrast_threshold: float = 25.0,
        rel_thresh: float = 0.25,
        clahe_clip: float = 3,
        clahe_grid: tuple = (8, 8)
) -> int:
    """
    读取单张图像，初筛 blob → CLAHE 增强 → 计算点-环境亮度差分布并打印 →
    二次筛查（绝对差 or 相对差）→ 标记并保存，返回计数
    """
    # 读取图像并提取红色通道
    img_bgr = cv2.imread(input_image_path, cv2.IMREAD_COLOR)
    if img_bgr is None:
        raise FileNotFoundError(f"无法读取文件: {input_image_path}")
    red = img_bgr[:, :, 2]

    # 高斯模糊降噪
    red_blur = cv2.GaussianBlur(red, (5, 5), 0)

    # CLAHE 自适应直方图均衡
    clahe = cv2.createCLAHE(clipLimit=clahe_clip, tileGridSize=clahe_grid)
    red_eq = clahe.apply(red_blur)

    # 初始化 SimpleBlobDetector 参数
    params = cv2.SimpleBlobDetector_Params()
    params.minThreshold = 100
    params.maxThreshold = 255
    params.filterByArea = True
    params.minArea = 25
    params.maxArea = 81
    params.filterByColor = True
    params.blobColor = 255
    params.filterByCircularity = False
    params.filterByInertia = False
    params.filterByConvexity = False
    params.minDistBetweenBlobs = min_distance_between_spots

    detector = cv2.SimpleBlobDetector_create(params)
    keypoints = detector.detect(red_eq)

    # 计算亮度差并打印分布
    h, w = red_eq.shape
    diffs_abs, diffs_rel, kp_data = [], [], []
    eps = 1e-6
    for kp in keypoints:
        x, y = int(kp.pt[0]), int(kp.pt[1])
        small_r = int(kp.size / 2)
        big_r = int(small_r * ambient_scale)

        # 跳过太靠边无法形成完整环
        if x - big_r < 0 or x + big_r >= w or y - big_r < 0 or y + big_r >= h:
            continue

        # 构造小圆和环形区域的 mask
        mask_small = np.zeros((h, w), dtype=np.uint8)
        cv2.circle(mask_small, (x, y), small_r, 255, -1)
        mask_big = np.zeros_like(mask_small)
        cv2.circle(mask_big, (x, y), big_r, 255, -1)
        mask_ring = cv2.subtract(mask_big, mask_small)

        m_small = cv2.mean(red_eq, mask=mask_small)[0]
        m_ambient = cv2.mean(red_eq, mask=mask_ring)[0]
        abs_diff = m_small - m_ambient
        rel_diff = m_small / (m_ambient + eps) - 1.0

        diffs_abs.append(abs_diff)
        diffs_rel.append(rel_diff)
        kp_data.append((x, y, small_r, abs_diff, rel_diff))

    # 打印差值分布及百分位数
    if diffs_abs:
        da, dr = sorted(diffs_abs), sorted(diffs_rel)
        print(f"[{os.path.basename(input_image_path)}] Abs diffs: {da[:5]} ... {da[-5:]}")
        print(f"[{os.path.basename(input_image_path)}] Rel diffs: {dr[:5]} ... {dr[-5:]}")
        print("Abs diffs percentiles:", np.percentile(diffs_abs, [10, 25, 50, 75, 90]))
        print("Rel diffs percentiles:", np.percentile(diffs_rel, [10, 25, 50, 75, 90]))

    # 二次筛查：绝对亮度差 or 相对亮度差
    accepted = [
        (x, y, r)
        for x, y, r, ad, rd in kp_data
        if ad >= contrast_threshold or rd >= rel_thresh
    ]

    # 标记并写入计数
    out = img_bgr.copy()
    for x, y, r in accepted:
        cv2.circle(out, (x, y), max(r, 5), (255, 0, 0), 1)
    count = len(accepted)
    cv2.putText(out, f"count number: {count}", (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
    cv2.imwrite(output_image_path, out)
    print(f"[{os.path.basename(input_image_path)}] → {count} dots saved to {output_image_path}\n")

    return count


if __name__ == "__main__":
    # 配置参数
    INPUT_FOLDER = "mito_img"
    BASE_OUTPUT = "output"
    MIN_DIST = 8.0             # 最小斑点分离距离 (px)
    AMBIENT_SCALE = 2.0        # 环形区域半径 / 小圆半径
    CONTRAST_THR = 25.0        # 绝对亮度差阈值
    REL_THR = 0.25             # 相对亮度差阈值 (25%)
    CLAHE_CLIP = 3             # CLAHE 剪切阈值
    CLAHE_GRID = (8, 8)        # CLAHE 网格尺寸
    BLOB_MIN_THR = 100         # Blob 最小灰度阈值
    BLOB_MAX_THR = 255         # Blob 最大灰度阈值
    BLOB_MIN_AREA = 25         # Blob 最小面积 (px^2)
    BLOB_MAX_AREA = 81         # Blob 最大面积 (px^2)

    # 创建输出子文件夹
    timestamp = datetime.now().strftime("%m%d%y_%H%M%S")
    out_folder = os.path.join(BASE_OUTPUT, timestamp)
    os.makedirs(out_folder, exist_ok=True)

    # 写入参数文件
    param_path = os.path.join(out_folder, "parameter and values.txt")
    with open(param_path, "w", encoding="utf-8") as f:
        f.write("Parameter                       Value     Description\n")
        f.write("--------------------------------------------------------\n")
        f.write(f"MIN_DIST                       {MIN_DIST:<8}  最小斑点分离距离 (px)\n")
        f.write(f"AMBIENT_SCALE                  {AMBIENT_SCALE:<8}  环形区域半径 / 小圆半径\n")
        f.write(f"CONTRAST_THR                   {CONTRAST_THR:<8}  绝对亮度差阈值\n")
        f.write(f"REL_THR                        {REL_THR:<8}  相对亮度差阈值\n")
        f.write(f"CLAHE_CLIP                     {CLAHE_CLIP:<8}  CLAHE 剪切阈值\n")
        f.write(f"BLOB_MIN_THR                   {BLOB_MIN_THR:<8}  Blob 最小灰度阈值\n")
        f.write(f"BLOB_MAX_THR                   {BLOB_MAX_THR:<8}  Blob 最大灰度阈值\n")
        f.write(f"BLOB_MIN_AREA                  {BLOB_MIN_AREA:<8}  Blob 最小面积 (px^2)\n")
        f.write(f"BLOB_MAX_AREA                  {BLOB_MAX_AREA:<8}  Blob 最大面积 (px^2)\n\n")
        f.write("Image counts:\n")

    # 批量处理并记录
    records = []
    for ext in ("*.png", "*.jpg", "*.jpeg", "*.tif", "*.tiff"):
        for img_path in glob.glob(os.path.join(INPUT_FOLDER, ext)):
            name, _ = os.path.splitext(os.path.basename(img_path))
            out_name = f"{name}_counted.jpg"
            out_path = os.path.join(out_folder, out_name)

            count = count_red_spots_with_contrast(
                input_image_path=img_path,
                output_image_path=out_path,
                min_distance_between_spots=MIN_DIST,
                ambient_scale=AMBIENT_SCALE,
                contrast_threshold=CONTRAST_THR,
                rel_thresh=REL_THR,
                clahe_clip=CLAHE_CLIP,
                clahe_grid=CLAHE_GRID
            )
            # 写入 Text
            with open(param_path, "a", encoding="utf-8") as f:
                f.write(f"{name}: {count}\n")
            records.append({"Image": name, "Count": count})

    # 导出 Excel
    df = pd.DataFrame(records)
    excel_path = os.path.join(out_folder, "image_counts.xlsx")
    df.to_excel(excel_path, index=False)
    print(f"Image counts saved to {excel_path}")
    print(f"全部图片处理完毕，结果保存在: {out_folder}")