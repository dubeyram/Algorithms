import os
import sys
from collections import defaultdict, deque

with open(os.path.join(os.path.dirname(__file__), 'input.txt')) as f:
    program = [int(x) for x in f.read().split(",")]


class VM:
    def __init__(self, program):
        self.pointer = 0
        self.program = defaultdict(int, enumerate(program))
        self.input = []
        self.output = []
        self.done = False
        self.base = 0

        self.op_params = {
            1: 3, 2: 3, 3: 1, 4: 1, 5: 2, 6: 2, 7: 3, 8: 3, 9: 1
        }

    def add_input(self, input):
        self.input.append(input)
        self.run()

    def run(self):
        while True:
            opcode = self.program[self.pointer]
            code = opcode % 100
            if code == 99:
                self.done = True
                return
            if code == 3 and len(self.input) == 0:
                return

            num_params = self.op_params[code]
            modes = [(opcode // 10**i) %
                     10 for i in range(2, 2+num_params)]
            args = [self.program[self.pointer+x]
                    for x in range(1, 1+num_params)]
            reads = [(self.program[a], a, self.program[a+self.base])[m]
                     for a, m in zip(args, modes)]
            writes = [(a, None, a+self.base)[m]
                      for a, m in zip(args, modes)]

            self.pointer += num_params + 1
            if code == 1:
                self.program[writes[2]] = reads[0] + reads[1]
            elif code == 2:
                self.program[writes[2]] = reads[0] * reads[1]
            elif code == 3:
                self.program[writes[0]] = self.input.pop(0)
            elif code == 4:
                self.output.append(reads[0])
            elif code == 5:
                if reads[0] != 0:
                    self.pointer = reads[1]
            elif code == 6:
                if reads[0] == 0:
                    self.pointer = reads[1]
            elif code == 7:
                self.program[writes[2]] = int(reads[0] < reads[1])
            elif code == 8:
                self.program[writes[2]] = int(reads[0] == reads[1])
            elif code == 9:
                self.base += reads[0]


vms = [VM(program) for _ in range(50)]
qs = defaultdict(deque)
qnat = deque([], maxlen=1)

for i, vm in enumerate(vms):
    vm.add_input(i)
    vm.add_input(-1)

part1_done = False
prevY = None
while True:
    idle = True
    for ivm, vm in enumerate(vms):
        if vm.done is True:
            assert False
            continue
        # queue prev messages
        out = vm.output[:]
        vm.output = []
        for offset in range(len(out)//3):
            msg = out[offset*3:(offset+1)*3]
            to, x, y = msg
            if to == 255:
                if part1_done is False:
                    print('part1: ', y)
                    part1_done = True
                qnat.append((x, y))
            else:
                qs[to].append((x, y))
                idle = False
        # feed quequed messages
        if qs[ivm]:
            idle = False
            x, y = qs[ivm].popleft()
            vm.add_input(x)
            vm.add_input(y)
        else:
            vm.add_input(-1)

    if idle:
        assert len(qnat) == 1
        if all(len(q) == 0 for q in qs.values()):
            x, y = qnat.popleft()
            if y == prevY:
                print('part2: ', y)
                sys.exit(0)
            prevY = y
            vms[0].add_input(x)
            vms[0].add_input(y)
