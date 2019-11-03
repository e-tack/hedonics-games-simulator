# Generateur de coalitions stables
# Implementation de l'algorithme setpart2 issue d'un article
# paru dans "The computer journal" en octobre 1988
# Code inspire de : https://github.com/mrqc/partitions-of-set


def generator(n):
    codeword = [1 for _ in range(0, n)]
    while True:
        yield tuple(codeword)
        startIndex = n - 1

        while startIndex >= 0:
            if codeword[0: startIndex]:
                maxValue = max(codeword[0: startIndex])
            else:
                return
            codewordAtStartIndex = codeword[startIndex]
            if (
                maxValue > n or
                codewordAtStartIndex > maxValue or
                codewordAtStartIndex >= n
            ):
                codeword[startIndex] = 1
                startIndex -= 1
            else:
                codeword[startIndex] += 1
                break


# Version memoisee du generateur
# Faire attention a l'usage de la ram
# Utilise ~8Go pour n = 12
# Ne fonctionne plus - TODO
memory = {}


def memo_generator(n):
    global memory
    g = generator(n)
    memory[n] = memory.get(n, [])
    print(len(memory))
    step = 0
    while True:
        try:
            if step >= len(memory[n]):
                memory[n].append(next(g))
            yield memory[n][step]
            step += 1
        except StopIteration:
            break
