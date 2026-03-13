#!/bin/bash
# Set Alpha Vantage API Key for macOS/Linux

echo "Setting Alpha Vantage API Key..."

# Add to .bashrc
echo 'export ALPHA_VANTAGE_API_KEY=JSET7HHTHBL8I5WM' >> ~/.bashrc

# Add to .zshrc (for macOS Catalina and newer)
echo 'export ALPHA_VANTAGE_API_KEY=JSET7HHTHBL8I5WM' >> ~/.zshrc

echo ""
echo "✓ API Key has been set!"
echo ""
echo "IMPORTANT: You must reload your shell for the change to take effect."
echo ""
echo "Next steps:"
echo "1. Run: source ~/.bashrc (for bash) or source ~/.zshrc (for zsh)"
echo "2. Or close and reopen your terminal"
echo "3. Navigate to backend folder: cd backend"
echo "4. Restart the backend: python -m uvicorn main:app --reload"
echo ""
echo "The API key will now be used automatically by the application."
echo ""
