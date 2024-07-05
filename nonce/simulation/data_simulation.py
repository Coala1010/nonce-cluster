import csv
from random import choices, gauss
import yaml
import pandas as pd
from config_set import *

# Define your range and parameters
MIN_NOISE = 0.1
MAX_NOISE = 0.5

class MonthlyData:
    
    def __init__(self, year, month, hr_distrubution):
        self.year = year
        self.month = month
        self.hr_distrubution = hr_distrubution
        self.sample_size = MONTH_LENGTHS[month] * DAY_BLOCK_SIZE

    def get_date(self):
        return f"{MONTH_NAMES[self.month]} {self.year}"

    def simulate_nonces(self):
        labeled_nonces = []
        for i in range(self.sample_size):
            asic_name = choices(list(self.hr_distrubution.keys()), weights=self.hr_distrubution.values())[0]
            asic = ASICs[asic_name]
            nonce = asic.generate_nonce()
            labeled_nonces.append([asic_name, nonce, self.year, self.month + 1, i])
        return labeled_nonces

    def compute_statistics(self):
        asic_count = {asic: 0 for asic in ASIC_NAMES}
        for nonce in self.nonces:
            asic_count[nonce[0]] += 1
        return asic_count

class ASIC:
    
    def __init__(self, name) -> None:
        self.name = name

    def initialize(self, b0_hole, b3_hole):
        self.generate_valid_vals(b0_hole, b3_hole)
        self.generate_probs()
        return self

    def generate_valid_vals(self, b0_hole, b3_hole):
        self.b0_valids = self.get_valid_vals(b0_hole)
        self.b3_valids = self.get_valid_vals(b3_hole)

    def get_valid_vals(self, hole):
        hole_set = set()
        for start, end in hole:
            hole_set.update(range(start, end + 1))
        return [i for i in range(128) if i not in hole_set]

    def generate_prob(self, valid_list):
        # Generate noise values
        if (self.name.lower() != "control"):
            random_values = [max(0, MIN_NOISE + (MAX_NOISE - MIN_NOISE) * abs(gauss(0, 1))) for _ in range(len(valid_list))]
        else:
            random_values = [1 / len(valid_list) for _ in range(len(valid_list))]

        # random_values = [max(0, gauss(0, 1)) for _ in range(len(valid_list))]
        sum_random_values = sum(random_values)
        normalized_values = [value / sum_random_values for value in random_values]
        return dict(zip(valid_list, normalized_values))
    
    def generate_probs(self):
        self.prob_b0 = self.generate_prob(self.b0_valids)
        self.prob_b3 = self.generate_prob(self.b3_valids)

    def make_choice(self, prob_dict):
        keys = list(prob_dict.keys())
        values = list(prob_dict.values())
        return choices(keys, weights=values, k=1)[0]

    def choose_b0_b3(self):
        b0 = self.make_choice(self.prob_b0) << 1 | choices([0, 1], k=1)[0]
        b3 = self.make_choice(self.prob_b3) << 1 | choices([0, 1], k=1)[0]
        return b0, b3
    
    def generate_nonce(self):
        b0, b3 = self.choose_b0_b3()
        b12 = choices(range(1 << 16), k=1)[0]
        return b0 << 24 | b12 << 8 | b3

def read_asic_patterns(filename):
    with open(filename, 'r') as file:
        return yaml.safe_load(file)

def save_to_excel(nonce_data, filename):
    df = pd.DataFrame(nonce_data, columns=['ASIC', 'Nonce', 'Year', 'Month', 'Index'])
    df.to_excel(filename, index=False)
    print("Data has been saved to", filename)

def process_monthly_data(csv_file):
    monthly_data_list = []
    with open(csv_file, 'r') as file:
        csv_reader = csv.reader(file)
        data = list(csv_reader)

    asic_names = [row[0].lower() for row in data[1:]]
    for i, month_data in enumerate(data[0][1:], 1):
        if "-" not in month_data:
            continue
        month, year = month_data.split("-")
        month_num = MONTH_NAMES.index(month)
        hr_distrubution = {asic_names[j]: float(data[j + 1][i]) if data[j + 1][i] else 0 for j in range(len(asic_names))}
        monthly_data = MonthlyData(int(year) + YEAR_OFFSET, month_num, hr_distrubution)
        monthly_data_list.append(monthly_data)
    return monthly_data_list

if __name__ == "__main__":
    asic_patterns = read_asic_patterns("asic_pattern.yaml")
    ASICs = {asic_name: ASIC(asic_name).initialize(asic_patterns['b0_hole'][asic_name], asic_patterns['b3_hole'][asic_name]) for asic_name in ASIC_NAMES}
    nonce_data = []

    for monthly_data in process_monthly_data("test_data.csv"):
        nonces = monthly_data.simulate_nonces()
        nonce_data.extend(nonces)
        print(monthly_data.get_date())
    
    save_to_excel(nonce_data, "simulated.xlsx")
