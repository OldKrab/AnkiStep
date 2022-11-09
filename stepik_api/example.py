from data_loader import DataLoader


loader = DataLoader()

quizes = loader.load_quizes(55014)
def print_q(q):
     print(q.step)
     print(q.attempt)
     print(q.submission)

list(map(print_q, quizes))