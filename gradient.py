def score_to_color(n: int) -> str:
    def hex_to_rgb(h: str):
        h = h.lstrip('#')
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

    def rgb_to_hex(rgb):
        return '#' + ''.join(f'{v:02X}' for v in rgb)

    positions = [-0.2, 0.4, 0.7, 1.0]
    hex_colors = [
        '#FF411A', # error
        '#FFD15C', # partial color 1
        '#BEDF81', # partial color 2
        '#7AAB79', # ac 100
    ]

    rgbs = [hex_to_rgb(h) for h in hex_colors]

    t = (n - 1) / 98

    if t <= positions[0]:
        r, g, b = rgbs[0]
    elif t >= positions[-1]:
        r, g, b = rgbs[-1]
    else:
        for i in range(len(positions) - 1):
            if positions[i] <= t < positions[i+1]:
                span = positions[i+1] - positions[i]
                u = (t - positions[i]) / span
                r0, g0, b0 = rgbs[i]
                r1, g1, b1 = rgbs[i+1]
                r = round((1 - u) * r0 + u * r1)
                g = round((1 - u) * g0 + u * g1)
                b = round((1 - u) * b0 + u * b1)
                break

    return rgb_to_hex((r, g, b))