
# Jyldam Jauap - Smart City Legal Assistant

## Overview
Jyldam Jauap is a smart city legal assistant application designed to provide legal information and assistance to businesses and individuals. The application offers features such as legal news, fines and taxes checker, lawyer database, and an AI-powered legal assistant.

## Features
- **Legal News**: Stay updated with the latest legal news and changes in legislation.
- **Fines and Taxes Checker**: Check for outstanding fines and taxes using IIN.
- **Lawyer Database**: Find qualified lawyers based on specialization and experience.
- **AI Legal Assistant**: Get instant legal advice and answers to your questions.

## Installation
1. **Clone the repository**:
    ```sh
    git clone https://github.com/AlanJumabayev/Project_For_Smart_City_V1
    cd Project_For_Smart_City_V1
    ```

2. **Install dependencies**:
    ```sh
    pip install -r requirements.txt
    ```

3. **Set up environment variables**:
    - Create a `.env` file in the project root directory.
    - Add your OpenAI API key to the `.env` file:
      ```
      OPENAI_API_KEY=your_openai_api_key
      ```

4. **Run the application**:
    ```sh
    python main.py
    ```

## Usage
- **Main Application**: Run `main.py` to start the main application interface.
- **Fines Checker**: Run `fines.py` to check for fines and taxes.
- **AI Legal Assistant**: Run `chat.py` to interact with the AI legal assistant.

## Directory Structure
```
Project_For_Smart_City_V1/
│
├── db/                     # Database files
├── images/                 # Image assets
│   ├── icon.ico            # Application icon
│   ├── logo.png            # Application logo
│   └── lawyers/            # Lawyer images
├── chat.py                 # AI Legal Assistant script
├── fines.py                # Fines and Taxes Checker script
├── main.py                 # Main application script
├── README.md               # Project documentation
└── requirements.txt        # Python dependencies
```

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request.

## License
This project is licensed under the [MIT License](LICENSE).
