import cv2
import numpy as np
from PIL import Image
import pyembroidery

def create_embroidery_from_image(image_file, format_ext="pes", width_mm=100, height_mm=100):
    """
    이미지를 업로드받아 지정된 사이즈(mm)의 자수 패턴으로 변환 후 바이너리 데이터를 반환합니다.
    """
    # 1. 이미지 로드 및 OpenCV BGR 포맷으로 변환
    img = Image.open(image_file).convert("RGB")
    img_cv = np.array(img)
    img_cv = img_cv[:, :, ::-1].copy()

    # 2. 흑백 변환 및 노이즈 제거
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # 3. 이진화(Adaptive Thresholding)로 선 추출 (어두운 선을 흰색으로)
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
    
    # 4. 윤곽선(Contours) 찾기
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        raise ValueError("이미지에서 선이나 그림을 찾을 수 없습니다. 조금 더 뚜렷한 그림을 올려주세요.")

    # 5. 스케일 계산 (pyembroidery는 기본적으로 0.1mm 단위(10 units = 1mm) 사용)
    max_width_units = width_mm * 10.0
    max_height_units = height_mm * 10.0

    all_points = np.vstack(contours).squeeze()
    if all_points.ndim == 1:
        # 점이 하나뿐인 경우 예외 처리
        min_x, min_y = all_points
        max_x, max_y = all_points
    else:
        min_x, min_y = all_points.min(axis=0)
        max_x, max_y = all_points.max(axis=0)

    img_width = max(max_x - min_x, 1)
    img_height = max(max_y - min_y, 1)

    # 지정된 hoop size에 맞게 여백을 10% 정도 남기고 스케일링
    scale = min(max_width_units / img_width, max_height_units / img_height) * 0.9

    # 6. 자수 패턴 생성
    pattern = pyembroidery.EmbPattern()

    for contour in contours:
        # 윤곽선을 부드럽게(단순화) 만들어 스티치 수 줄이기
        epsilon = 0.005 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        
        points = approx.squeeze()
        if points.ndim == 1:
            points = [points]
            
        if len(points) < 2:
            continue
            
        first = True
        for pt in points:
            x, y = pt
            # 중심을 맞추고 스케일 적용
            px = (x - min_x - img_width / 2) * scale
            py = (y - min_y - img_height / 2) * scale
            
            if first:
                # 첫 점으로 이동 (Jump)
                pattern.add_stitch_absolute(pyembroidery.JUMP, px, py)
                first = False
            else:
                # 선 따라가기 (Stitch)
                pattern.add_stitch_absolute(pyembroidery.STITCH, px, py)

    if len(pattern.stitches) == 0:
        raise ValueError("유효한 자수 경로를 생성하지 못했습니다.")

    # 7. 파일로 내보내기 (메모리에서 읽기)
    out_file = f"temp_output.{format_ext}"
    pyembroidery.write(pattern, out_file)
    
    with open(out_file, "rb") as f:
        data = f.read()
        
    return data
