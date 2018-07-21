# This file is part of the Smali Emulator.
#
# Copyright(c) 2016 Simone 'evilsocket' Margaritelli
# evilsocket@gmail.com
# http://www.evilsocket.net
#
# This file may be licensed under the terms of of the
# GNU General Public License Version 3 (the ``GPL'').
#
# Software distributed under the License is distributed
# on an ``AS IS'' basis, WITHOUT WARRANTY OF ANY KIND, either
# express or implied. See the GPL for the specific language
# governing rights and limitations.
#
# You should have received a copy of the GPL along with this
# program. If not, go to http://www.gnu.org/licenses/gpl.html
# or write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
from __future__ import print_function
from __future__ import division

import ast
import re
import struct

# TODO: Implement missing opcodes.

# Base class for all Dalvik opcodes ( see http://pallergabor.uw.hu/androidblog/dalvik_opcodes.html ).
class OpCode(object):
    trace = False

    def __init__(self, expression):
        self.expression = re.compile(expression)

    @staticmethod
    def get_int_value(val):
        val = val.rstrip('t')  # for byte elements
        val = val.rstrip('s')  # for short elements
        return ast.literal_eval(val)

    def parse(self, line, vm):
        m = self.expression.search(line)
        if m is None:
            return False

        if OpCode.trace is True:
            print("%03d %s" % (vm.pc, line))

        try:
            self.eval(vm, *[x.strip() if x is not None else x for x in m.groups()])
        except Exception as e:
            vm.exception(e)

        return True

    @staticmethod
    def eval(vm, *args):
        """Implementation must be declared in the corresponding opcode class.

        - vm stores the current vm state.
        - args is the list of argument for this op code."""
        raise NotImplementedError()


class op_Const(OpCode):
    """Evaluate a constant object."""
    def __init__(self):
        OpCode.__init__(self, '^const(?:/\d+)? (.+),\s*(.+)')

    @staticmethod
    def eval(vm, vx, lit):
        vm[vx] = OpCode.get_int_value(lit)


class op_ConstString(OpCode):
    """Evaluate a constant string."""
    def __init__(self):
        OpCode.__init__(self, '^const-string(?:/jumbo)? (.+),\s*"(.*)"')

    @staticmethod
    def eval(vm, vx, s):
        vm[vx] = s.encode('utf-8')


class op_Move(OpCode):
    """Evaluate a move."""
    def __init__(self):
        OpCode.__init__(self, '^move(?:-object)? (.+),\s*(.+)')

    @staticmethod
    def eval(vm, vx, vy):
        vm[vx] = vm[vy]


class op_MoveResult(OpCode):
    """MoveResult"""
    def __init__(self):
        OpCode.__init__(self, '^move-result(?:-object)? (.+)')

    @staticmethod
    def eval(vm, dest):
        vm[dest] = vm.return_v


class op_MoveException(OpCode):
    def __init__(self):
        OpCode.__init__(self, '^move-exception (.+)')

    @staticmethod
    def eval(vm, vx):
        vm[vx] = vm.exceptions.pop()


class op_IfLe(OpCode):
    def __init__(self):
        OpCode.__init__(self, '^if-le (.+),\s*(.+),\s*(\:.+)')

    @staticmethod
    def eval(vm, vx, vy, label):
        if vm[vx] <= vm[vy]:
            vm.goto(label)


class op_IfGe(OpCode):
    def __init__(self):
        OpCode.__init__(self, '^if-ge (.+),\s*(.+),\s*(\:.+)')

    @staticmethod
    def eval(vm, vx, vy, label):
        if vm[vx] >= vm[vy]:
            vm.goto(label)


class op_IfGez(OpCode):
    def __init__(self):
        OpCode.__init__(self, '^if-gez (.+),\s*(\:.+)')
        
    @staticmethod
    def eval(vm, vx, label):
        if vm[vx] >= 0:
            vm.goto(label)


class op_IfLtz(OpCode):
    def __init__(self):
        OpCode.__init__(self, '^if-ltz (.+),\s*(\:.+)')
        
    @staticmethod
    def eval(vm, vx, label):
        if vm[vx] < 0:
            vm.goto(label)


class op_IfGt(OpCode):
    def __init__(self):
        OpCode.__init__(self, '^if-gt (.+),\s*(.+),\s*(\:.+)')

    @staticmethod
    def eval(vm, vx, vy, label):
        if vm[vx] > vm[vy]:
            vm.goto(label)


class op_IfGtz(OpCode):
    def __init__(self):
        OpCode.__init__(self, '^if-gtz (.+),\s*(\:.+)')
        
    @staticmethod
    def eval(vm, vx, label):
        if vm[vx] > 0:
            vm.goto(label)


class op_IfLez(OpCode):
    def __init__(self):
        OpCode.__init__(self, '^if-lez (.+),\s*(\:.+)')

    @staticmethod
    def eval(vm, vx, label):
        if vm[vx] <= 0:
            vm.goto(label)


class op_IfEq(OpCode):
    def __init__(self):
        OpCode.__init__(self, '^if-eq (.+),\s*(.+),\s*(\:.+)')

    @staticmethod
    def eval(vm, vx, vy, label):
        if vm[vx] == vm[vy]:
            vm.goto(label)


class op_IfNe(OpCode):
    def __init__(self):
        OpCode.__init__(self, '^if-ne (.+),\s*(.+),\s*(\:.+)')

    @staticmethod
    def eval(vm, vx, vy, label):
        if vm[vx] != vm[vy]:
            vm.goto(label)


class op_IfLt(OpCode):
    def __init__(self):
        OpCode.__init__(self, '^if-lt (.+),\s*(.+),\s*(\:.+)')

    @staticmethod
    def eval(vm, vx, vy, label):
        if vm[vx] < vm[vy]:
            vm.goto(label)


class op_IfEqz(OpCode):
    def __init__(self):
        OpCode.__init__(self, '^if-eqz (.+),\s*(\:.+)')

    @staticmethod
    def eval(vm, vx, label):
        if vm[vx] == 0:
            vm.goto(label)


class op_IfNez(OpCode):
    def __init__(self):
        OpCode.__init__(self, '^if-nez (.+),\s*(\:.+)')

    @staticmethod
    def eval(vm, vx, label):
        if vm[vx] != 0:
            vm.goto(label)


class op_ArrayLength(OpCode):
    def __init__(self):
        OpCode.__init__(self, 'array-length (.+),\s*(.+)')

    @staticmethod
    def eval(vm, vx, vy):
        vm[vx] = len(vm[vy])


class op_ArrayFillData(OpCode):
    def __init__(self):
        OpCode.__init__(self, 'fill-array-data (.+),\s*(.+)')

    @staticmethod
    def eval(vm, vx, label):
        vm[vx] = vm.array_data[label]["elements"]


class op_Aget(OpCode):
    def __init__(self):
        OpCode.__init__(self, '^aget[\-a-z]* (.+),\s*(.+),\s*(.+)')

    @staticmethod
    def eval(vm, vx, vy, vz):
        arr     = vm[vy]
        idx     = vm[vz]
        vm[vx] = arr[idx]


class op_AddIntLit(OpCode):
    def __init__(self):
        OpCode.__init__(self, '^add-int/lit\d+ (.+),\s*(.+),\s*(.+)')

    @staticmethod
    def eval(vm, vx, vy, lit):
        vm[vx] = eval( "%s + %s" % ( vm[vy], lit ) )


class op_MulIntLit(OpCode):
    def __init__(self):
        OpCode.__init__(self, '^mul-int/lit\d+ (.+),\s*(.+),\s*(.+)')

    @staticmethod
    def eval(vm, vx, vy, lit):
        vm[vx] = eval("%s * %s" % (vm[vy], lit))


class op_XorInt2Addr(OpCode):
    def __init__(self):
        OpCode.__init__(self, '^xor-int(?:/2addr)? (.+),\s*(.+)')

    @staticmethod
    def eval(vm, vx, vy):
        # test if vm[vy] is a char instead of an int
        if isinstance(vm[vy], int):
            vm[vx] ^= int(vm[vy])
        else:
            vm[vx] ^= ord(vm[vy])


class op_XorIntLit(OpCode):
    #xor-int/lit8 v0, v0, 0x26

    def __init__(self):
        OpCode.__init__(self, '^xor-int/lit\d+ (.+),\s*(.+),\s*(.+)')

    @staticmethod
    def eval(vm, vx, vy, lit):
        if isinstance(vm[vy],int):
            ii = int(vm[vy])
        else:
            ii = ord(vm[vy])
        vm[vx] = ii ^ OpCode.get_int_value(lit)


class op_OrIntLiteral(OpCode):

    def __init__(self):
        OpCode.__init__(self, '^or-int/lit(\d+) (.+),\s*(.+),\s*(.+)')

    @staticmethod
    def eval(vm, size, vx, vy, literal):
        """
        >>> vm = {'v0': 1, 'v1': 2, 'v2': 16}
        >>> op_OrIntLiteral.eval(vm, 8, 'v2', 'v1', '0x3')
        >>> vm == {'v0': 1, 'v1': 2, 'v2': (0x3 | vm['v1'])}
        True
        """
        if isinstance(vm[vy],int):
            ii = int(vm[vy])
        else:
            ii = ord(vm[vy])
        vm[vx] = ii | OpCode.get_int_value(literal)


class op_DivIntLit(OpCode):
    def __init__(self):
        OpCode.__init__(self, '^div-int/lit\d+ (.+),\s*(.+),\s*(.+)')

    @staticmethod
    def eval(vm, vx, vy, lit):
        vm[vx] = vm[vy] // OpCode.get_int_value(lit)


class op_DivInt(OpCode):
    def __init__(self):
        OpCode.__init__(self, '^div-int (.+),\s*(.+),\s*(.+)')

    @staticmethod
    def eval(vm, vx, vy, vz):
        vm[vx] = vm[vy] // vm[vz]


class op_DivIntLit(OpCode):
    def __init__(self):
        OpCode.__init__(self, '^div-int/lit\d+ (.+),\s*(.+),\s*(.+)')

    @staticmethod
    def eval(vm, vx, vy, lit):
        vm[vx] = vm[vy] // OpCode.get_int_value(lit)


class op_AddInt(OpCode):
    def __init__(self):
        OpCode.__init__(self, '^add-int (.+),\s*(.+),\s*(.+)')

    @staticmethod
    def eval(vm, vx, vy, vz):
        vm[vx] = vm[vy] + vm[vz]


class op_SubInt(OpCode):
    def __init__(self):
        OpCode.__init__(self, '^sub-int (.+),\s*(.+),\s*(.+)')

    @staticmethod
    def eval(vm, vx, vy, vz):
        vm[vx] = vm[vy] - vm[vz]


class op_MulInt(OpCode):
    def __init__(self):
        OpCode.__init__(self, '^mul-int (.+),\s*(.+),\s*(.+)')

    @staticmethod
    def eval(vm, vx, vy, vz):
        vm[vx] = vm[vy] * vm[vz]


class op_RemInt(OpCode):
    def __init__(self):
        OpCode.__init__(self, '^rem-int (.+),\s*(.+),\s*(.+)')

    @staticmethod
    def eval(vm, vx, vy, vz):
        vm[vx] = vm[vy] % vm[vz]


class op_AndInt(OpCode):
    def __init__(self):
        OpCode.__init__(self, '^and-int (.+),\s*(.+),\s*(.+)')

    @staticmethod
    def eval(vm, vx, vy, vz):
        vm[vx] = vm[vy] & vm[vz]


class op_AndIntLit(OpCode):
    def __init__(self):
        OpCode.__init__(self, '^and-int/lit\d+ (.+),\s*(.+),\s*(.+)')

    @staticmethod
    def eval(vm, vx, vy, lit):
        vm[vx] = int(vm[vy]) & OpCode.get_int_value(lit)


class op_AndInt2Addr(OpCode):
    def __init__(self):
        OpCode.__init__(self, '^and-int/2addr (.+),\s*(.+)')

    @staticmethod
    def eval(vm, vx, vy):
        """
        >>> vm = {'v0': 0xff, 'v1': 0xf0}
        >>> op_AndInt2Addr.eval(vm, 'v0', 'v1')
        >>> vm == {'v0': 0xf0, 'v1': 0xf0}
        True
        """
        vm[vx] = int(vm[vy]) & int(vm[vx])


class op_OrInt(OpCode):
    def __init__(self):
        OpCode.__init__(self, '^or-int (.+),\s*(.+),\s*(.+)')

    @staticmethod
    def eval(vm, vx, vy, vz):
        vm[vx] = vm[vy] | vm[vz]


class op_ShlIntLit(OpCode):
	#shl-int/lit8 vx, vy, lit8
    def __init__(self):
        OpCode.__init__(self, '^shl-int/lit\d+ (.+),\s*(.+),\s*(.+)')

    @staticmethod
    def eval(vm, vx, vy, lit):
        vm[vx] = vm[vy] << OpCode.get_int_value(lit)
	

class op_GoTo(OpCode):
    def __init__(self):
        OpCode.__init__(self, '^goto(?:/\d+)? (:.+)')

    @staticmethod
    def eval(vm, label):
        vm.goto(label)


class op_NewInstance(OpCode):
    def __init__(self):
        OpCode.__init__(self, '^new-instance (.+),\s*(.+)')

    @staticmethod
    def eval(vm, vx, klass):
        vm[vx] = vm.new_instance(klass)


class op_NewArray(OpCode):
    def __init__(self):
        OpCode.__init__(self, '^new-array (.+),\s*(.+),\s*(.+)')

    @staticmethod
    def eval(vm, vx, vy, klass):
        vm[vx] = [""] * vm[vy]


class op_APut(OpCode):
    def __init__(self):
        OpCode.__init__(self, '^aput(?:-[a-z]+)? (.+),\s*(.+),\s*(.+)')

    @staticmethod
    def eval(vm, vx, vy, vz):
        idx = int(vm[vz])
        arr = vm[vy]
        val = vm[vx]
        if len(arr) > idx:
            arr[idx] = val
        elif idx == len(arr):
            arr.append(val)
        vm[vy] = arr


class op_Invoke(OpCode):
    def __init__(self):
        OpCode.__init__(self, '^invoke-(?:[a-z]+) \{(.*)\},\s*(.+)')

    @staticmethod
    def eval(vm, args, call):
        args = list(map(str.strip, args.split(',')))
        this = args[0]
        args = args[1:]
        klass, method  = call.split(';->')

        vm.invoke(this, klass, method, args)


class op_IntToType(OpCode):
    def __init__(self):
        OpCode.__init__(self, '^int-to-([a-z]+) (.+),\s*(.+)')

    @staticmethod
    def eval(vm, ctype, vx, vy):
        if ctype == 'char':
            vm[vx] = chr(vm[vy] & 0xFFFF)
        elif ctype == 'byte' :
            vm[vx] = struct.pack('>i', vm[vy])[-1]
        else:
            vm.emu.fatal("Unsupported type '%s' ." % ctype)


class op_SPut(OpCode):
    def __init__(self):
        OpCode.__init__(self, '^sput(?:-[a-z]+)?\s+(.+),\s*(.+)')

    @staticmethod
    def eval(vm, vx, staticVariableName):
        vm.variables[staticVariableName] = vm.variables[vx]


class op_SGet(OpCode):
    def __init__(self):
        OpCode.__init__(self, '^sget(?:-[a-z]+)?\s+(.+),\s*(.+)')

    @staticmethod
    def eval(vm, vx, staticVariableName):
        vm.variables[vx] = vm.variables[staticVariableName]


class op_Return(OpCode):
    def __init__(self):
        OpCode.__init__(self, '^return(-[a-z]*)*\s*(.+)*')

    @staticmethod
    def eval(vm, ctype, vx):
        if (ctype is None and vx is None) or ctype == '-void':
            vm.return_v = None
            vm.stop = True
        elif ctype in ( '-wide', '-object' ) or (ctype is None and vx is not None):
            vm.return_v = vm[vx]
            vm.stop = True

        else:
            vm.emu.fatal("Unsupported return type.")


class op_RemIntLit(OpCode):
    def __init__(self):
        OpCode.__init__(self, '^rem-int/lit\d+ (.+),\s*(.+),\s*(.+)')

    @staticmethod
    def eval(vm, vx, vy, lit):
        vm[vx] = int(vm[vy]) % OpCode.get_int_value(lit)


class op_PackedSwitch(OpCode):
    def __init__(self):
        OpCode.__init__(self, '^packed-switch (.+),\s*(.+)')

    @staticmethod
    def eval(vm, vx, table):
        val = vm[vx]
        switch = vm.packed_switches.get(table, {})
        cases = switch.get('cases', [])
        case_idx = val - switch.get('first_value')

        if case_idx >= len(cases) or case_idx < 0:
            return

        case_label = cases[case_idx]

        vm.goto(case_label)

class op_RSubIntLiteral(OpCode):
    def __init__(self):
        OpCode.__init__(self, '^rsub-int/lit(\d+) (.+),\s*(.+),\s*(.+)')

    @staticmethod
    def eval(vm, register_size, destination, source, constant):
        """
        >>> vm = {'v0': 1, 'v1': 2, 'v2': 4}
        >>> # perform v1 - 0x3 and store the result into v2
        >>> op_RSubIntLiteral.eval(vm, 8, 'v2', 'v1', '0x3')
        >>> vm  # v2 is 0x3 - v1 = 0x3 - 2 = 1
        {'v0': 1, 'v1': 2, 'v2': 1}
        """
        register_size = int(register_size)  # 8, 16 or 32 bytes
        source = vm[source]
        constant = OpCode.get_int_value(constant)
        result = constant - source
        assert all(-(2 ** (register_size - 1)) <= x <= (2 ** (register_size - 1) - 1)
                   for x in (source, constant, result))
        vm[destination] = result

class op_RSubInt(OpCode):
    def __init__(self):
        OpCode.__init__(self, '^rsub-int\s+(.+),\s*(.+),\s*(.+)')

    @staticmethod
    def eval(vm, destination, source, constant):
        """
        >>> vm = {'v0': 1, 'v1': 2, 'v2': 4}
        >>> # perform v1 - 0x3 and store the result into v2
        >>> op_RSubInt.eval(vm, 'v2', 'v1', '0x32')
        >>> vm  # v2 is 0x32 - v1 = 0x32 - 2 = 48
        {'v0': 1, 'v1': 2, 'v2': 48}
        """
        source = vm[source]
        constant = OpCode.get_int_value(constant)
        result = constant - source
        vm[destination] = result


class op_AddInt2Addr(OpCode):
    def __init__(self):
        OpCode.__init__(self, r'^add-int/2addr (.+),\s*(.+)')

    @staticmethod
    def eval(vm, source_and_dest, source_register):
        """
        >>> vm = {'v0': 1, 'v1': 2, 'v2': 4}
        >>> # perform v1 + v2 and store the result into v1
        >>> op_AddInt2Addr.eval(vm, 'v1', 'v2')
        >>> vm
        {'v0': 1, 'v1': 6, 'v2': 4}
        """
        source1 = vm[source_register]
        source2 = vm[source_and_dest]
        result = source1 + source2
        vm[source_and_dest] = result


class op_SubInt2Addr(OpCode):
    def __init__(self):
        OpCode.__init__(self, r'^sub-int/2addr (.+),\s*(.+)')

    @staticmethod
    def eval(vm, source_and_dest, source_register):
        """
        >>> vm = {'v0': 1, 'v1': 2, 'v2': 4}
        >>> # perform v1 + v2 and store the result into v1
        >>> op_SubInt2Addr.eval(vm, 'v1', 'v2')
        >>> vm
        {'v0': 1, 'v1': -2, 'v2': 4}
        """
        source1 = vm[source_register]
        source2 = vm[source_and_dest]
        result = source2 - source1
        vm[source_and_dest] = result


class op_OrInt2Addr(OpCode):
    def __init__(self):
        OpCode.__init__(self, r'^or-int/2addr (.+),\s*(.+)')

    @staticmethod
    def eval(vm, source_and_dest, source_register):
        """
        >>> vm = {'v0': 1, 'v1': 2, 'v2': 4}
        >>> op_OrInt2Addr.eval(vm, 'v1', 'v2')
        >>> vm == {'v0': 1, 'v1': (2 | 4), 'v2': 4}
        True
        >>> op_OrInt2Addr.eval(vm, 'v0', 'v1')
        >>> vm == {'v0': (1 | 2 | 4), 'v1': (2 | 4), 'v2': 4}
        True
        """
        source1 = vm[source_register]
        source2 = vm[source_and_dest]
        result = source1 | source2
        vm[source_and_dest] = result


class op_NegInt(OpCode):
    def __init__(self):
        OpCode.__init__(self, r'^neg-int (.+),\s*(.+)')

    @staticmethod
    def eval(vm, dest, source):
        """
        >>> vm = {'v0': 1, 'v1': 2}
        >>> # perform v0 + v1 and store the result into v0
        >>> op_AddInt2Addr.eval(vm, 'v0', 'v1')
        >>> vm
        {'v0': 3, 'v1': 2}
        """
        vm[dest] = -vm[source]


