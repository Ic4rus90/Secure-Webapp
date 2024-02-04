from app import create_app

app = create_app()


if __name__ == "__main__":
    # debug=True makes Python errors appear on the web page.
    app.run(debug=True, use_reloader=False)

