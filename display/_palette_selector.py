from myhdl import block, always_comb


@block
def palette_selector(sel, color, rgb):
    
    black = int('00000000', 2)
    green = int('00011100', 2)
    red = int('11100000', 2)
    beige = int('11111101', 2)
    light_purple = int('11100001', 2)
    aquamarine = int('00011101', 2)
    orange = int('11101100', 2)
    blue = int('00000011', 2)
    yellow = int('11111100', 2)
    teal = int('00011111', 2)

    palette0 = (green, light_purple, red, orange, aquamarine, teal, yellow,
                 teal, light_purple, blue, aquamarine, green, red, beige,
                green, green)
    palette1 = (red, aquamarine, yellow, blue, light_purple, orange,
                light_purple, red, aquamarine, orange, red, light_purple,
                blue, light_purple, red, red)
    palette2 = (beige, orange, aquamarine, aquamarine, yellow, blue, green,
                yellow, red, aquamarine, beige, red, yellow, green, beige,
                beige)
    
    @always_comb
    def foo():
        rgb.next = black
        if color == 1:
            rgb.next = palette0[sel]
        elif color == 2:
            rgb.next = palette1[sel]
        elif color == 3:
            rgb.next = palette2[sel]
    return foo
