# scripts/run_multiseed.ps1
param(
  [Parameter(Mandatory=$true)][string]$ScenarioYaml,   # e.g., configs/scenarios/collusion_attack.yaml
  [int]$Seeds = 10,
  [string]$Tag = "multiseed"
)

# Example command placeholder. Replace with YOUR actual run command.
# It must accept: --config <yaml> and --seed <int> and --run-name <string>
function Run-One($seed, $runName) {
  python -m src.main --config $ScenarioYaml --seed $seed --run-name $runName
}

for ($s=0; $s -lt $Seeds; $s++) {
  $runName = "{0}_{1}_seed{2:00}" -f $Tag, (Split-Path $ScenarioYaml -LeafBase), $s
  Write-Host "Running $ScenarioYaml seed=$s -> $runName"
  Run-One $s $runName
}