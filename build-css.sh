#!/bin/bash
# Build script for TailwindCSS

echo "Building TailwindCSS for production..."
npx tailwindcss -i ./static/css/input.css -o ./static/css/output.css --minify
echo "TailwindCSS build complete!"

echo "Updating browserslist database..."
npx update-browserslist-db@latest
echo "Build process finished!"
