# CLI Operations Reference

## Daily
```bash
tsar scan .                 # local scan before commit
tsar drift                  # check upstream version
```

## Per Release
```bash
tsar scan . --format sarif --output results.sarif
tsar report . --format html --output release-report.html
tsar compliance soc2
```

## Weekly
```bash
tsar drift
tsar lint
```

## Initial Setup
```bash
tsar init . --agent cursor
tsar init . --agent claude
```