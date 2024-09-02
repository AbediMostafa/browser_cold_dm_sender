import os
from time import sleep
from script.models.Lead import Lead
from script.extra.adapters.SettingAdapter import SettingAdapter
import random
import string

import numpy as np
from skimage import io, util, transform, exposure
from pathlib import Path
from PIL import Image
import os
from random import randint


def pause(_min, _max):
    sleep(randint(_min, _max))


def test_accounts():
    from spintax import spin

    leads = Lead.select().where(Lead.id.in_([36979, 23365, 23366]))
    for lead in leads:
        lead.dm_text = spin(SettingAdapter.cold_dm_spintax())

    return leads


def get_post_path(template_path):
    project_path = Path(__file__).parent.parent.parent
    return os.path.join(project_path, 'backend', 'storage', 'app', 'public', template_path)


def image_manipulator(path):
    # Load the image using skimage
    image = io.imread(path)

    # Apply Gaussian noise
    noisy_image = util.random_noise(image, mode='gaussian', var=0.01)

    # Apply a slight rotation
    rotated_image = transform.rotate(noisy_image, angle=randint(1, 10), mode='wrap')

    # Adjust brightness and contrast
    adjusted_image = exposure.adjust_gamma(rotated_image, gamma=0.9)

    # Convert the image to uint8 (8-bit unsigned integer)
    adjusted_image_uint8 = (adjusted_image * 255).astype(np.uint8)

    # Save the image temporarily with skimage
    temp_path = 'temp_image.png'
    io.imsave(temp_path, adjusted_image_uint8)

    # Open the image with PIL to handle RGBA to RGB conversion
    with Image.open(temp_path) as img:
        # Convert RGBA to RGB if necessary
        if img.mode == 'RGBA':
            img = img.convert('RGB')

        # Save the final image as JPEG
        output_path = 'generated_image.jpg'
        img.save(output_path)

    # Clean up the temporary image
    os.remove(temp_path)

    project_path = Path(__file__).parent.parent
    return os.path.join(project_path, output_path)


def chat_ai(prompt, max_tokens=400, temperature=0.7, top_p=1.0, frequency_penalty=0.0, presence_penalty=0.0):
    from openai import OpenAI

    # Set your API key
    client = OpenAI(api_key='')

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty)

        return response.choices[0].message.content
    except Exception as e:
        raise Exception(e)


def get_random_user_agent():
    import random

    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:88.0) Gecko/20100101 Firefox/88.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.864.48 Safari/537.36 Edg/91.0.864.48",
        "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.818.56 Safari/537.36 Edg/90.0.818.56",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36 OPR/74.0.3911.160",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36 OPR/73.0.3856.344",
        "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0",
        "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.705.81 Safari/537.36 Edg/88.0.705.81",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 11.2; rv:86.0) Gecko/20100101 Firefox/86.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 11.2.3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36 Edg/89.0.774.63",
        "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36 OPR/71.0.3770.284",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0"
    ]

    return random.choice(user_agents)


def generate_password(length=10):
    characters = string.ascii_letters + string.digits
    password = ''.join(random.choice(characters) for _ in range(length))
    return password
