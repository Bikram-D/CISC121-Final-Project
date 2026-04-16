import gradio as gr
import time

# Step 1: Parse input text into list of tuples
def parse_input(text):
    stops = []
    lines = text.strip().split("\n")

    for line in lines:
        # Skips empty lines
        if not line.strip():
            continue

        # Makes sure each line has a comma seperating the stop name and crowd count
        if "," not in line:
            raise ValueError("Each line must contain a comma.")

        parts = line.split(",")

        # Makes sure each line has both parts, the stop name and crowd count
        if len(parts) != 2:
            raise ValueError("Each line must have exactly one comma.")

        name = parts[0].strip()
        count_str = parts[1].strip()

        # Checks that the crowd count is a non-negative integer
        if not count_str.isdigit():
            raise ValueError(f"Invalid number: '{count_str}'. Must be a non-negative integer.")

        stops.append((name, int(count_str)))

    return stops


# Format list into format of (name, count)
def format_list(items):
    if not items:
        return "[]"
    return ", ".join([f"{name} ({count})" for name, count in items])


# Step 2: Merge function
def merge(left, right, steps):
    merged = []
    i = 0
    j = 0

    # Compares elements from both halves
    while i < len(left) and j < len(right):
        if left[i][1] >= right[j][1]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1

    # Adds remaining elements from left side
    while i < len(left):
        merged.append(left[i])
        i += 1

    # Adds remaining elements from right side
    while j < len(right):
        merged.append(right[j])
        j += 1

    # Saves the step for the visual step output
    steps.append({
        "left": left,
        "right": right,
        "merged": merged
    })

    return merged


# Step 3: Merge sort
def merge_sort(arr, steps):
    if len(arr) <= 1:
        return arr

    mid = len(arr) // 2

    # Split into left and right halves
    left = merge_sort(arr[:mid], steps)
    right = merge_sort(arr[mid:], steps)

    # Merge sorted halves
    return merge(left, right, steps)


# Step 4: Run sorting and animate the steps for sorting
def run_sort(text):
    try:
        stops = parse_input(text)

        if len(stops) == 0:
            yield "No valid data entered.", ""
            return

        steps = []
        sorted_stops = merge_sort(stops, steps)

        log_text = ""

        # Builds the step by step visualization
        for idx, step in enumerate(steps):
            left_str = format_list(step['left'])
            right_str = format_list(step['right'])
            merged_str = format_list(list(step['merged']))

            # Makes the step by step output readable
            log_text += f"Step {idx + 1}:\n"
            log_text += f"  Left: {left_str}\n"
            log_text += f"  Right: {right_str}\n"
            log_text += f"  Merged: {merged_str}\n\n"

            # Update sent to UI after each step
            yield log_text, ""
            time.sleep(2)

        # Final output
        final_result = "\n".join([f"{name} ({count})" for name, count in (sorted_stops)])

        yield log_text, final_result

    except Exception as e:
        yield f"Error: {str(e)}", ""


# Step 5: Gradio GUI 
with gr.Blocks() as app:
    gr.Markdown("""
    # 🚍 Shuttle Stop Crowd Ranking

    Enter data in the format with one entry per line:
    **stop_name, crowd_count**  
    (Ensure crowd_count values are non-negative integers.)
    """)

    with gr.Row():
        with gr.Column():
            input_box = gr.Textbox(label="Input Stop Data", lines=10)
            run_button = gr.Button("Run Merge Sort")

        with gr.Column():
            steps_log = gr.Textbox(label="Merge Sort Step View", lines=35)
            final_output = gr.Textbox(label="Final Ranking (Most Crowded First)")

    run_button.click(
        fn=run_sort,
        inputs=input_box,
        outputs=[steps_log, final_output]
    )


# Step 6: Launch app
if __name__ == "__main__":
    app.launch()