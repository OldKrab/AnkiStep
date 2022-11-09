from data_loader import DataLoader


loader = DataLoader()

id = 128197
id = 91


quizes = loader.load_quizes(id)
def print_q(q):
     print(q.step)
     print()
     print(q.attempt)
     print()
     print(q.submission)
     print()


list(map(print_q, quizes))
