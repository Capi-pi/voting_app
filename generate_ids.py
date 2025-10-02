import random
import string
import csv
import os

CHARS = string.ascii_letters + string.digits
ID_FILE = "ids.csv"

# Charger les IDs existants
def load_ids(file=ID_FILE):
    if not os.path.exists(file):
        return set()
    with open(file, newline="") as f:
        return set(row[0] for row in csv.reader(f))

# Sauver un ID
def save_id(new_id):
    with open(ID_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([new_id])

def generate_unique_id(length=4):
    generated_ids = load_ids()
    while True:
        new_id = ''.join(random.choices(CHARS, k=length))
        if new_id not in generated_ids:
            save_id(new_id)
            return new_id

def main():
    N_STUDENT = 130

    for _ in range(N_STUDENT):
        generate_unique_id()


if __name__ == "__main__":
    print(load_ids())