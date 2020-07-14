import BitVector

def bytes2bits(data):
    bits = []
    for b in data:
        bits.append(BitVector.BitVector(intVal=b, size=8).reverse())
    return bits
