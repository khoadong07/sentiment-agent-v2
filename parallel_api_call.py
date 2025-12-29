import requests
import json
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import time

def call_analyze_api(row):
    """Single API call function"""
    url = "http://0.0.0.0:4880/analyze"
    headers = {'Content-Type': 'application/json'}
    data = {
        "id": str(row.get('Id', '')),
        "index": str(row.get('TopicId', '')),
        "topic": str(row.get('Topic', '')),
        "title": str(row.get('Title', '')),
        "content": str(row.get('Content', '')),
        "description": str(row.get('Description', '')),
        "type": str(row.get('Type', '')),
        "main_keywords": ["spx express", "spxexpress", "shopee express", "spx"]
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data), timeout=30)
        if response.status_code == 200:
            result = response.json()
            return row.name, result.get('sentiment', '')  # Return index and result
        else:
            print(f"API error for row {row.name}: Status {response.status_code}")
            return row.name, ''
    except Exception as e:
        print(f"Exception for row {row.name}: {str(e)}")
        return row.name, ''

def process_dataframe_parallel(df, max_workers=10):
    """
    Process dataframe with parallel API calls
    
    Args:
        df: pandas DataFrame with data
        max_workers: Number of parallel threads (default: 10)
    
    Returns:
        DataFrame with 'Verify Sentiment' column added
    """
    print(f"Processing {len(df)} rows with {max_workers} parallel workers...")
    
    # Initialize result column
    df['Verify Sentiment'] = ''
    
    # Create list of rows for processing
    rows_to_process = [row for _, row in df.iterrows()]
    
    start_time = time.time()
    completed_count = 0
    
    # Process with ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_row = {executor.submit(call_analyze_api, row): row for row in rows_to_process}
        
        # Process completed tasks with progress bar
        with tqdm(total=len(rows_to_process), desc="API Calls") as pbar:
            for future in as_completed(future_to_row):
                try:
                    row_index, sentiment = future.result()
                    df.loc[row_index, 'Verify Sentiment'] = sentiment
                    completed_count += 1
                    pbar.update(1)
                except Exception as e:
                    print(f"Error processing future: {str(e)}")
                    pbar.update(1)
    
    elapsed_time = time.time() - start_time
    print(f"Completed {completed_count}/{len(df)} API calls in {elapsed_time:.2f} seconds")
    print(f"Average time per call: {elapsed_time/len(df):.2f} seconds")
    
    return df

# Usage example:
if __name__ == "__main__":
    # Assuming you have filtered_data DataFrame
    # filtered_data = process_dataframe_parallel(filtered_data, max_workers=10)
    
    # Example with sample data
    sample_data = pd.DataFrame({
        'Id': ['1', '2', '3'],
        'TopicId': ['topic1', 'topic2', 'topic3'],
        'Topic': ['SPX Express', 'SPX Express', 'SPX Express'],
        'Title': ['Test title 1', 'Test title 2', 'Test title 3'],
        'Content': ['Test content 1', 'Test content 2', 'Test content 3'],
        'Description': ['Test desc 1', 'Test desc 2', 'Test desc 3'],
        'Type': ['fbGroupTopic', 'fbGroupTopic', 'fbGroupTopic']
    })
    
    # Process with parallel calls
    result_df = process_dataframe_parallel(sample_data, max_workers=5)
    print(result_df[['Id', 'Verify Sentiment']])