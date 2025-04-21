from functools import partial

from discord.ui import View, Button


class TestView(View):
    def __init__(self):
        super().__init__()

        async def cb(interaction, x: int = 0):
            await interaction.response.send_message(f"Button {x} pressed")

        for x in range(0, 5):
            button = Button(label=f"Button {x}")
            button.callback = partial(cb, x=x)
            self.add_item(button)
