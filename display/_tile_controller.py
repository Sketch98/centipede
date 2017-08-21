from myhdl import always, always_comb, block, Signal, intbv, concat

from simple_components import delay_cycles
from utils import RamPort


@block
def tile_brom(clk, addr, data):
    @always(clk)
    def foo():
        pass

    assert len(addr) == 12, 'addr width = {}, should be 10'.format(len(addr))
    assert len(data) == 2, 'data width = {}, should be 4'.format(len(data))
    clk.read = True
    addr.read = True
    data.driven = True
    return foo
tile_brom.vhdl_code = """
--copy this signal declaration to architecture declaration
signal ${data}_slv : std_logic_vector(1 downto 0);

${data} <= unsigned(${data}_slv);
tile_rom: entity work.tile_brom
    port map (
        clka    => $clk,
        addra   => std_logic_vector($addr),
        douta   => ${data}_slv);
"""


@block
def tile_ram(
        # ports and interfaces
        clk,
        write_port,
        read_port):
    depth = 1024
    assert len(write_port.data) == len(read_port.data),\
        'font ram data widths do not match\n dina width {}, doutb width {}'\
        .format(len(write_port.data), len(read_port.data))
    assert len(write_port.addr) == 10,\
        'font ram addresses must be 10\n ' \
        'write addr width {}'.format(len(write_port.addr))
    assert len(read_port.addr) == 10,\
        'font ram addresses must be 10\n ' \
        'read addr width {}'.format(len(read_port.addr))
    assert 2 ** (len(write_port.addr) - 1) < depth\
        <= 2 ** (len(write_port.addr))
    width = len(write_port.data)
    
    ram = [Signal(intbv(0)[width:]) for _ in range(depth)]
    
    @always(clk.posedge)
    def read():
        read_port.data.next = ram[int(read_port.addr)]
    
    @always(clk.posedge)
    def write():
        if write_port.en:
            ram[int(write_port.addr)].next = write_port.data
    
    return read, write


@block
def tile_controller(
        # ports and interfaces
        clk,
        x,
        y,
        ram_write_port,
        tile_color):
    rom_addr = Signal(intbv(0)[12:])
    rom_data = Signal(intbv(0)[2:])
    rom = tile_brom(clk, rom_addr, rom_data)
    
    ram_read_port = RamPort(1024, 6)
    ram = tile_ram(clk, ram_write_port, ram_read_port)
    
    x_delayed = Signal(intbv(0)[3:])
    y_delayed = Signal(intbv(0)[3:])
    delay_x = delay_cycles(clk, x(3, 0), x_delayed)
    delay_y = delay_cycles(clk, y(3, 0), y_delayed)
    
    @always_comb
    def foo():
        ram_read_port.addr.next = concat(y[8:3], x[8:3])
        rom_addr.next = concat(ram_read_port.data, y_delayed, x_delayed)
        tile_color.next = rom_data
    
    return rom, ram, foo, delay_x, delay_y
