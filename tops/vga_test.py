import os

from myhdl import Signal, block, intbv

from vga import vga_timer, n_bit_color
from utils import VgaSignals, VgaPorts, ucf_gen


@block
def vga_test(clk, vga_ports, resolution, frequency):
    """A myhdl top for testing vga_timer on nexys2_1200. Outputs a constant
    image on a monitor at 800x600 pixels at 72fps. """
    vga_signals = VgaSignals(resolution)
    timer = vga_timer(clk, vga_signals, resolution, frequency, (160, 160, 44, 44))
    color = n_bit_color(clk, vga_signals.x(8, 0), vga_signals, vga_ports)
    return timer, color

if __name__ == "__main__":
    clk = Signal(bool(0))
    vga_ports = VgaPorts(3, 3, 2)
    vga_top_inst = vga_test(clk, vga_ports, (800, 600), 72)
    vga_top_inst.convert(hdl='VHDL')
    this_dir = os.path.dirname(__file__)
    vhd_file = '/'.join([this_dir, 'vga_test.vhd'])
    ucf_gen(vhd_file, 'nexys2_1200.ucf')
