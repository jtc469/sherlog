# SherLog

## Getting the data

### LONL
`https://csr.lanl.gov/data/cyber1/)`

LONL data comes in the form of 5 .gz files, totalling ~10GB.

Load each file with wget in a different tmux pane

`cd ~/sherlog/data`
`BASE="https://csr.lanl.gov/data-fence/1792003970/UseQ-7ppnHx3Y5G_9V8D6L4b108=/cyber1"`
`wget -c -O proc.txt.gz "$BASE/proc.txt.gz"`

Repeat for redteam, dns, flows, auth