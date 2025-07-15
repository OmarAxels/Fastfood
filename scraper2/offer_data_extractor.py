import g4f
import json

with open("kfc_menu.md", "r", encoding="utf-8") as f:
    menu_text = f.read()

    prompt = f"""
    You are a helpful assistant that extracts offers data from a menu.

    Extract the following data:
    - Offer name
    - Offer description
    - Offer price
    - Offer link
    Return the data in a JSON format.

    The menu is:
    {menu_text}
    """ 

    response = g4f.ChatCompletion.create(
          model="gpt-4o-mini",
      messages=[
          {"role": "system", "content": prompt},
          {"role": "user", "content": menu_text}
      ]
    )

    print(response)
    with open("result.json", "w", encoding="utf-8") as f:
        json.dump(response, f, indent=4, default=str)