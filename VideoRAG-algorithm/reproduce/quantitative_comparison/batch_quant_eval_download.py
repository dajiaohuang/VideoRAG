import json
import os

os.environ.setdefault("OPENAI_API_KEY", "")

from openai import OpenAI


def obtain_ouput_file_id(batches, client=None):
    if client is None:
        client = OpenAI()
    for batch in batches:
        batch_info = client.batches.retrieve(batch)
        print(batch_info)
        print(batch_info.output_file_id)


def download_result(result_files, base_dir, client=None):
    if client is None:
        client = OpenAI()

    for file_id in result_files:
        content = client.files.content(file_id).content
        temp_path = f"batch_requests/{base_dir}/{file_id}.temp"
        result_path = f"batch_requests/{base_dir}/{file_id}.json"
        try:
            with open(temp_path, "wb") as f:
                f.write(content)
            results = []
            with open(temp_path, "r", encoding="utf-8") as f:
                for line in f:
                    results.append(json.loads(line.strip()))
            with open(result_path, "w", encoding="utf-8") as json_file:
                json.dump(results, json_file, indent=4)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)


# Please enter the relevant batch ID here to obtain the output file ID.
batches = [
    "",
    "",
    "",
    "",
    "",
]


def main():
    obtain_ouput_file_id(batches)
    # Second Step: enter output file IDs below and call:
    # download_result(result_files, base_dir="overall_comparison_video_understanding")


if __name__ == "__main__":
    main()
