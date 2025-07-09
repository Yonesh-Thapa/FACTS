with app.app_context():
    deadline = SiteSetting.query.filter_by(key="early_bird_deadline").first()
    if deadline:
        parsed = deadline.parsed_value
        print(f"Parsed deadline: {parsed}")
        print(f"JS format: {parsed.strftime("%B %d, %Y %H:%M:%S")}")
        print(f"Display format: {parsed.strftime("%B %d")}")
        print(f"Days until deadline: {(parsed - datetime.now()).days}")
    else:
        print("No deadline setting found")
