import json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Patch
from datetime import datetime
from collections import defaultdict
from gradient import score_to_color
import argparse

parser = argparse.ArgumentParser(description="Plot problem statistics from standings data.")
parser.add_argument(
    "--data-file", 
    type=str, 
    default="standings_data.json", 
    help="Path to the JSON file containing standings data (default: standings_data.json)"
)
parser.add_argument(
    "--save", 
    action="store_true", 
    help="Save the plots as PNG files"
)
parser.add_argument(
    "--show",
    action="store_true",
    help="Show the plots interactively"
)
args = parser.parse_args()

DATA_FILE = args.data_file
SAVE = args.save
SHOW = args.show
try:
    with open(DATA_FILE, "r") as file:
        data = json.load(file)
except (FileNotFoundError, json.JSONDecodeError):
    print("Scrape data before plotting. If you have a valid data file use --data-file to specify it.")
    exit(1)

timestamps = [entry["timestamp"] for entry in data]
results = [entry["results"] for entry in data]

times = [datetime.fromisoformat(ts) for ts in timestamps]

problems_data = defaultdict(list)
for timestamp, result in zip(times, results):
    for participant, problems in result.items():
        for problem, details in problems.items():
            score = int(details["score"])
            tries = details["tries"]
            problems_data[problem].append((timestamp, participant, score, tries))

def calculate_changes(problem_data):
    changes = []
    prev_scores = {}
    prev_attempts = {}
    for timestamp, participant, score, tries in problem_data:
        if participant in prev_scores:
            prev_score = prev_scores[participant]
        else:
            prev_score = 0
        if prev_score != score or tries != prev_attempts: # only plot changes
            changes.append((timestamp, participant, score, tries))
        prev_scores[participant] = score
        prev_attempts[participant] = tries
    return changes

# plot each problem
for problem, problem_data in problems_data.items():
    changes = calculate_changes(problem_data)
    if not changes:
        continue

    fig, ax = plt.subplots(figsize=(12, 6))
    fig.suptitle(f'Problem: {problem}', fontsize=14)

    change_counts = defaultdict(lambda: {"100p": 0, "0p_with_try": 0})
    for timestamp, participant, score, tries in changes:
        if score == 100:
            change_counts[timestamp]["100p"] += 1
        elif 1 <= score < 100:
            if str(score) not in change_counts[timestamp]:
                change_counts[timestamp][str(score)] = 0
            change_counts[timestamp][str(score)] += 1
        elif score == 0 and tries != "0":
            change_counts[timestamp]["0p_with_try"] += 1

    all_timestamps = sorted(set(times))
    change_timestamps = sorted(change_counts.keys())

    # Plot changes
    bar_width = 0.02
    for timestamp in all_timestamps:
        if timestamp in change_counts:
            counts = change_counts[timestamp]
            ax.bar(timestamp, counts["100p"], width=bar_width, color='#9cd09d', label='100p' if timestamp == change_timestamps[0] else "")
            p = 0
            for i in range(99, 0, -1):
                if str(i) in counts:
                    color_partial = score_to_color(i)
                    ax.bar(timestamp, counts[str(i)], width=bar_width, color=color_partial, label=f'{i}p' if timestamp == change_timestamps[0] else "", bottom=counts["100p"]+p)
                    p += counts[str(i)]
            ax.bar(timestamp, counts["0p_with_try"], width=bar_width, color='#ff411a', label='0p with try' if timestamp == change_timestamps[0] else "", bottom=counts["100p"] + p)#counts["1-99p"])
        else:
            pass

    
    score_labels = set()
    for counts in change_counts.values():
        score_labels.update([k for k in counts.keys() if k not in ("100p","0p_with_try")])
    score_labels = sorted(score_labels, key=lambda x: int(x))

    legend_handles = [ Patch(facecolor='#9cd09d', label='100p') ]
    for score in score_labels:
        legend_handles.append(
            Patch(facecolor=score_to_color(int(score)), label=f'{score}p')
        )
    legend_handles.append( Patch(facecolor='#ff411a', label='0p with try') )

    ax.legend(handles=legend_handles, loc='upper left')

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
    plt.xticks(rotation=45)
    plt.xlabel('Time')
    plt.ylabel('Number of Changes')
    plt.title(f'Changes in Scores for Problem: {problem}')

    plt.tight_layout()
    if SAVE:
        plt.savefig(f'problem_{problem}.png', bbox_inches='tight')
    if SHOW:
        plt.show()