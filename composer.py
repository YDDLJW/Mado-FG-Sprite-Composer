import os
from PIL import Image
from metadata import get_image_position


def compose_images(body_path, expr_path):
    body_pos = get_image_position(body_path)
    expr_pos = get_image_position(expr_path)

    with Image.open(body_path) as body_im:
        body = body_im.convert("RGBA")
    with Image.open(expr_path) as expr_im:
        expr = expr_im.convert("RGBA")

    dx = expr_pos["x"] - body_pos["x"]
    dy = expr_pos["y"] - body_pos["y"]

    min_x = min(0, dx)
    min_y = min(0, dy)
    max_x = max(body.width, dx + expr.width)
    max_y = max(body.height, dy + expr.height)

    canvas_w = max_x - min_x
    canvas_h = max_y - min_y

    canvas = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    body_x = -min_x
    body_y = -min_y
    expr_x = dx - min_x
    expr_y = dy - min_y

    canvas.alpha_composite(body, (body_x, body_y))
    canvas.alpha_composite(expr, (expr_x, expr_y))

    return canvas, body_pos, expr_pos


def make_output_name(body_path, expr_path):
    body_name = os.path.splitext(os.path.basename(body_path))[0]
    expr_name = os.path.splitext(os.path.basename(expr_path))[0]
    return f"{body_name}__{expr_name}.png"


def combine_one(body_path, expr_path, output_dir):
    canvas, body_pos, expr_pos = compose_images(body_path, expr_path)
    out_name = make_output_name(body_path, expr_path)
    out_path = os.path.join(output_dir, out_name)
    canvas.save(out_path)
    return out_path, body_pos, expr_pos