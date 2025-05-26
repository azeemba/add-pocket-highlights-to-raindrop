# Add Pocket Highlights to Raindrop

Raindrop supports importing Pocket's data for links but no way to support highlights.
The data didn't exist till recently so its not surprising.

This project uses the raindrop APIs to upload the highlights.


1. You will need to create a developer application at https://app.raindrop.io/settings/integrations
2. Then follow the official instructions: "Just go to [App Management Console](https://app.raindrop.io/settings/integrations) and open your application settings. Copy Test token."
3. Write `TOKEN=[token]` (where you replace "[token]" with the token from the previous step) to a file name `.env`
4. Set up your python environment (only need requests python module). Example instructions: 
```sh
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
5. `python main.py [path to pocket highlights file]`

## Possible problems

- Raindrop is conservative in rate limits. You only have 120 requests and we need 2 requests per URL. So if there are more than 60 URLs, you will time out and will have to split the original JSON file.