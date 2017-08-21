import os

from myhdl import Signal, block, intbv, always_comb

from vga import vga_timer, n_bit_color
from utils import VgaSignals, VgaPorts, ucf_gen, RamPort
from display import tile_controller, palette_selector
from simple_components import clk_div, counter, delay_cycles


@block
def palette_test(clk, vga_ports, sw, resolution, frequency):
    """A myhdl top for testing vga_timer on nexys2_1200. Outputs a constant
    image on a monitor at 800x600 pixels at 72fps. """
    vga_signals = VgaSignals(resolution)
    timer = vga_timer(clk, vga_signals, resolution, frequency,
                      (160, 160, 44, 44))
    
    # delay control signals by 2 cycles to compensate for ram and rom
    delayed_vga_sigs = VgaSignals(resolution)
    sigs = [vga_signals.h_sync, vga_signals.v_sync, vga_signals.video_on]
    delayed_sigs = [delayed_vga_sigs.h_sync, delayed_vga_sigs.v_sync,
                    delayed_vga_sigs.video_on]
    delays = [delay_cycles(clk, sigs[i], delayed_sigs[i], 2)
              for i in range(len(sigs))]
    
    ram_write_port = RamPort(1024, 6)
    x = Signal(intbv(0)[8:])
    y = Signal(intbv(0)[8:])
    tile_color = Signal(intbv(0)[2:])
    tiles = tile_controller(clk, x, y, ram_write_port, tile_color)

    rgb = Signal(intbv(0)[8:])
    palette = palette_selector(sw, tile_color, rgb)
    color = n_bit_color(clk, rgb, delayed_vga_sigs, vga_ports)
    
    write_clk = Signal(bool(0))
    div = clk_div(5e3, clk, write_clk)
    screen_crawler = counter(write_clk, ram_write_port.addr, en=Signal(True))
    
    @always_comb
    def write_switches():
        ram_write_port.en.next = True
        ram_write_port.data.next = ram_write_port.addr[6:]
        
        x.next = vga_signals.x.next[9:1]
        y.next = vga_signals.y.next[9:1]
    
    return tiles, timer, color, delays, div, screen_crawler, write_switches,\
        palette


if __name__ == "__main__":
    clk = Signal(bool(0))
    vga_ports = VgaPorts(3, 3, 2)
    sw = Signal(intbv(0)[4:])
    vga_top_inst = palette_test(clk, vga_ports, sw, (800, 600), 72)
    vga_top_inst.convert(hdl='VHDL')
    this_dir = os.path.dirname(__file__)
    vhd_file = '/'.join([this_dir, 'palette_test.vhd'])
    ucf_gen(vhd_file, 'nexys2_1200.ucf')
