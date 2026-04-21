from typing import List

import discord
from discord import Embed, Color, ButtonStyle, SelectOption
from discord.ui import Button, Select, View
from pydantic import BaseModel

from Utils.database.database import PgDB, DfDB


class UserBaitInventory(BaseModel):
    bait_id: int
    name: str
    effectiveness: float
    quantity: int

class FishingState(BaseModel):
    owner_id: int
    selected_bait_id: int

class FishingHelper:
    FISHING_STATE_TTL_SECONDS: int = 5 * 60

    @staticmethod
    async def load_user_bait_inventory(user_id: int) -> List[UserBaitInventory]:
        async with PgDB() as db:
            cursor = await db.get_cursor()

            await cursor.execute("""
                SELECT ubi.bait_id, bt.name, bt.effectiveness, ubi.quantity
                FROM user_bait_inventory as ubi
                JOIN bait_types bt ON ubi.bait_id = bt.bait_id
                WHERE ubi.user_id = %s AND ubi.quantity > 0
                ORDER BY bt.price
            """, (user_id,))

            rows = await cursor.fetchall()

            return [
                UserBaitInventory(
                    bait_id = row[0],
                    name = row[1],
                    effectiveness = row[2],
                    quantity = row[3]
                )
                for row in rows
            ]

    @staticmethod
    def build_fishing_bait_select_embed(user_baits: List[UserBaitInventory]) -> Embed:
        if len(user_baits) == 0:
            return Embed(
                title = "🎣 Select Your Bait",
                description = "You have no bait! Use `baitshop to buy some.",
                color = Color.from_str("#ff4444")
            )

        bait_list = [f"""
            🪱 **{bait.name}** - {bait.quantity}x ({bait.effectiveness}x effectiveness\n"""
            for bait in user_baits
        ]

        return Embed(
            title = "🎣 Select Your Bait",
            description = [f"""
                Chose which bait you want to use for fishing:\n
                {bait_list}\n
                Different baits have different effectiveness multipliers!
                """
            ],
            color = Color.from_str("#2b7cff")
        )

    @staticmethod
    def build_fishing_bait_select_components(user_baits: List[UserBaitInventory], state: FishingState = None) -> View:
        view = View()

        if len(user_baits) == 0:
            cancel_btn = Button(
                custom_id = "fishing:cancel",
                label = "Close",
                style = ButtonStyle.secondary,
            )

            view.add_item(cancel_btn)

            return view

        bait_select = Select(
            custom_id = "fishing:bait_select",
            placeholder = "Choose your bait",
            options = [
                SelectOption(
                    label = f"{bait.name} ({bait.quantity}x)",
                    value = str(bait.bait_id),
                    description = f"{bait.effectiveness}x effectiveness",
                    default = state.selected_bait_id == bait.bait_id,
                )
                for bait in user_baits
            ]
        )
        view.add_item(bait_select)

        confirm_btn = Button(
            custom_id = "fishing:confirm",
            label = "🎣 Go Fishing!",
            style = ButtonStyle.primary,
            disabled = not (state and state.selected_bait_id),
        )

        cancel_btn = Button(
            custom_id="fishing:cancel",
            label="Close",
            style=ButtonStyle.secondary,
        )

        view.add_item(confirm_btn)
        view.add_item(cancel_btn)

        return view

    @classmethod
    async def save_fishing_state(cls, user_id, message_id, state):
        key = f"fishing:state:{user_id}:{message_id}"
        async with DfDB() as df:
            await df.set(key, state, ex = cls.FISHING_STATE_TTL_SECONDS)

class FishingBaitSelect(View):
    def __init__(self, user_id: int, user_baits: List[UserBaitInventory], state: FishingState):
        super().__init__(timeout=5*60)  # 5 minutes timeout
        self.user_id = user_id
        self.state = state
        self.user_baits = user_baits

        # Add the select menu
        self.add_item(self.BaitSelect(user_baits))

        # Add confirm and cancel buttons
        self.add_item(self.ConfirmButton())
        self.add_item(self.CancelButton())

    class BaitSelect(Select):
        def __init__(self, user_baits: List[UserBaitInventory]):
            options = [
                SelectOption(
                    label=bait.name,
                    value=str(bait.id),
                    description=f"{bait.description} (x{bait.quantity})"
                )
                for bait in user_baits
            ]
            super().__init__(
                placeholder="Select your bait...",
                min_values=1,
                max_values=1,
                options=options,
                custom_id="fishing:select_bait"
            )

        async def callback(self, interaction: discord.Interaction):
            view: FishingBaitSelect = self.view
            if interaction.user.id != view.user_id:
                await interaction.response.send_message(
                    "This fishing UI isn't yours. Use `/fish` to start your own.",
                    ephemeral = True,
                )
                return

            view.state.selected_bait_id = int(self.values[0])

            await FishingHelper.save_fishing_state(
                view.user_id,
                interaction.message.id,
                view.state
            )

            embed = FishingHelper.build_fishing_bait_select_embed(view.user_baits)
            await interaction.response.edit_message(embed = embed, view = view)




