import pandas as pd
import json

class DataLoader():

    def __init__(self, file_name):
        self.data = json.load(open(file_name, encoding="utf-8"))

        self.year = int(self.data["event"])
        self.users = []
        self.id = int(self.data["owner_id"])

        for _, member in enumerate(self.data["members"]):
            self.users.append(User(self.data["members"][member]))

        self.n_users = len(self.users)
        self.user_table = self.create_table()
        self.current_user_table = self.create_current_table()


    def create_table(self):
        user_table = pd.DataFrame(columns=["name", "id", "day", "part", "get_star_ts"])
        for user in self.users:
            user_table = pd.concat([user_table, user.star_table])

        user_table = user_table.sort_values(["day", "part", "get_star_ts"])
        user_table["cumulative_stars"] = user_table.groupby(["id"])["get_star_ts"].rank(method="first").astype(int)
        user_table["local_score"] = self.n_users + 1 - user_table.groupby(["day", "part"])["get_star_ts"].rank(method="first").astype(int)
        user_table["cumulative_local_score"] = user_table.groupby(["id"])["local_score"].cumsum()
        user_table["time"] = pd.to_datetime(user_table["get_star_ts"], unit="s")

        return user_table


    def create_current_table(self):
        current_user_table = self.user_table[["id", "name", "cumulative_stars", "cumulative_local_score"]]
        current_user_table = current_user_table.groupby(["id"]).max().sort_values(["cumulative_local_score"])
        current_user_table["rank_stars"] = current_user_table["cumulative_stars"].rank(method="min", ascending=False).astype(int)
        current_user_table["rank_local_score"] = current_user_table["cumulative_local_score"].rank(method="min", ascending=False).astype(int)

        return current_user_table


    def get_top_n_users(self, n, score_type = "local_score", label = "name"):
        assert score_type in ["local_score", "stars"], "Invalid choice of score to order by"
        assert label in ["name", "id"], "Invalid choice of display name"
        return self.current_user_table[self.data.current_user_table[f"rank_{score_type}"] <= n][label].tolist()[::-1]


    def __repr__(self) -> str:
        return f"Year: {self.year} | Number of users: {self.n_users} | Board ID: {self.id}"


class User():

    def __init__(self, user_data):
        self.name = user_data["name"]
        self.id = user_data["id"]
        self.stars = user_data["stars"]
        self.local_score = user_data["local_score"]
        self.global_score = user_data["global_score"]
        self.star_list = user_data["completion_day_level"]

        self.star_table = self.create_table()

    def create_table(self):
        star_table = []
        for day in self.star_list:
            for part in self.star_list[day]:
                star_table.append([self.name, self.id, int(day), int(part), self.star_list[day][part]["get_star_ts"]])
        return pd.DataFrame(star_table, columns=["name", "id", "day", "part", "get_star_ts"])

    def __repr__(self) -> str:
        return f"Name: {self.name} | ID: {self.id} | Stars: {self.stars} | Local score: {self.local_score}"

if __name__ == "__main__":
    loader = DataLoader(file_name="./data/2022.json")
    print(loader.user_table)