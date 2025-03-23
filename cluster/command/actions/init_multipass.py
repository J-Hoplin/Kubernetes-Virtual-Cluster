import sys
import subprocess
from cluster.utils import logger


def check_and_download_image(ubuntu_version):
    """
    1. Multipass에서 명시된 ubuntu 버전 이미지를 지원하는지 확인
    2. 이미지가 없는 경우 다운로드
    3. 이미지 버전은 설치된 multipass에서 지원하는 버전을 따라야함
    """
    image_name = f"{ubuntu_version}"
    log_context = "Multipass"

    try:
        result = subprocess.run(
            ["multipass", "find"], capture_output=True, text=True, check=True
        )
        available_images = result.stdout

        if image_name in available_images:
            logger.log(
                f"Ubuntu {image_name} is already available in host machine",
                context=log_context,
            )
            return image_name

        logger.log(
            f"Ubuntu {image_name} not found. Attempting to download...",
            context=log_context,
        )
        subprocess.run(["multipass", "find", image_name], check=True)
        logger.log(f"Ubuntu {image_name} prepared!", context=log_context)

    except subprocess.CalledProcessError as e:
        logger.error(
            f"Error: Unable to find or download Ubuntu {ubuntu_version} image."
        )
        logger.error(f"Error details: {e}")
        sys.exit(1)
