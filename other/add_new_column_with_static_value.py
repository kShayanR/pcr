import pandas as pd

def add_source_column(csv_file_path, output_file_path):
    try:
        df = pd.read_csv(csv_file_path)
        df['source'] = 'TripAdvisor'
        df.to_csv(output_file_path, index=False)
        print(f"The 'source' column has been added and saved to {output_file_path}")
    
    except FileNotFoundError:
        print(f"The file {csv_file_path} does not exist.")
    except pd.errors.EmptyDataError:
        print(f"The file {csv_file_path} is empty.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    csv_file_path = 'datasets/details_old.csv'
    output_file_path = 'datasets/details.csv'
    add_source_column(csv_file_path, output_file_path)
