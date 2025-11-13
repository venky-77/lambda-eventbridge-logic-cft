from jinja2 import Environment, FileSystemLoader
import yaml
import os
import subprocess

# Get list of changed parameter files using git
def get_changed_files():
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return [line.strip() for line in result.stdout.splitlines() if line.startswith("team_configs/parameters_")]
    except subprocess.CalledProcessError as e:
        print("⚠️ Git diff failed:", e.stderr)
        return []

# Setup Jinja2
env = Environment(loader=FileSystemLoader('./templates'))
template = env.get_template('lambda-eventbridge-template.yaml.j2')

# Ensure output directory exists
os.makedirs('output', exist_ok=True)

# Only process changed parameter files
changed_files = get_changed_files()
if not changed_files:
    print("✅ No parameter files changed. Skipping template generation.")
else:
    for param_file in changed_files:
        with open(param_file) as f:
            configs = yaml.safe_load(f)

        for config in configs:
            base_name = f"{config['schema_name']}-{config['table_name']}"
            output = template.render(**config)

            output_path = f"output/lambda-eb-{base_name}.yaml"
            with open(output_path, 'w') as f:
                f.write(output)

            print(f"✅ Rendered: {output_path} from {param_file}")