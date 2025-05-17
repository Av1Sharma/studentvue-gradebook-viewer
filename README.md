# StudentVue Gradebook Viewer

A Streamlit web application that allows students to view their grades from StudentVue in a clean, modern interface.

## Features

- Secure login with StudentVue credentials
- View current grades and marking period grades
- See detailed grade breakdowns
- Check recent assignments and scores
- Clean, modern UI with responsive design

## Local Development

1. Clone the repository:
```bash
git clone https://github.com/yourusername/studentvue-gradebook-viewer.git
cd studentvue-gradebook-viewer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the app locally:
```bash
streamlit run app.py
```

## Deployment on Streamlit Cloud

1. Fork this repository to your GitHub account
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Click "New app"
4. Select your forked repository
5. Set the main file path to `app.py`
6. Click "Deploy"

## Security Note

This application handles sensitive student credentials. When deploying:
- Never commit the `.env` file
- Use Streamlit's secrets management for production credentials
- Consider implementing additional security measures like rate limiting

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 