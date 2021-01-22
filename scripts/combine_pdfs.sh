plit files, note the naming scheme
pdfseparate File1.pdf temp-%04d-file1.pdf
pdfseparate File2.pdf temp-%04d-file2.pdf

# Combine the final pdf
pdfjam temp-*-*.pdf --nup 2x1 --landscape --outfile File1+2.pdf

# Clean up
rm -f temp-*-*.pdf
