#!/usr/bin/env bash
# Dump the image on the macOS clipboard to a PNG file.
# Prints the absolute file path on success, or "ERR_NO_IMAGE" when the
# clipboard holds no image. macOS only — uses osascript, no extra install.
set -euo pipefail

out="${TMPDIR:-/tmp}/claude-analyze-image-clipboard.png"
rm -f "$out"

result="$(osascript 2>/dev/null <<EOF || echo FAIL
set outFile to POSIX file "$out"
try
	set pngData to (the clipboard as «class PNGf»)
on error
	return "ERR_NO_IMAGE"
end try
set fh to open for access outFile with write permission
set eof fh to 0
write pngData to fh
close access fh
return "OK"
EOF
)"

if [ "$result" = "OK" ] && [ -s "$out" ]; then
	printf '%s\n' "$out"
else
	rm -f "$out"
	printf 'ERR_NO_IMAGE\n'
fi
