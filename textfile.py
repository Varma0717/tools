input_file = "generated_headlines.txt"
output_file = "headlines_quoted.txt"

with open(input_file, "r") as fin, open(output_file, "w") as fout:
    for line in fin:
        line = line.strip()
        if line:
            fout.write(f'"{line}",\n')
print("Done! Saved to", output_file)
