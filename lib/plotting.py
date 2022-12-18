import matplotlib.pyplot as plt

class Plotting():

    def __init__(
        self, 
        data,
        width = 20,
        height = 10
    ):
        self.data = data
        plt.rcParams['figure.figsize'] = [width, height]

    def plot_score_time_line(
        self,
        score_type = "local_score",
        n_top_users = None,
        users = None,
        label = "name"
    ):
        assert score_type in ["local_score", "stars"], "Invalid choice of score"
        assert label in ["name", "id"], "Invalid choice of display name"

        if isinstance(n_top_users, int):
            assert n_top_users > 0, "You have to choose a positive number of users"
            if isinstance(users, list):
                print(f"You provided both a list of users and to show the top {n_top_users} users. Choosing the latter.")
            users = self.data.get_top_n_users(n_top_users, label=label)
        elif isinstance(users, list):
            pass
        else:
            n_top_users = 5
            print(f"You provided neither a list of users nor to show the top n users. Choosing to show the top {n_top_users} users.")
            users = self.data.get_top_n_users(n_top_users, label=label)
        
        for user in users:
            current_user_table = self.data.user_table[self.data.user_table[label] == user]
            plt.step(
                current_user_table["time"], 
                current_user_table[f"cumulative_{score_type}"], 
                "-*", 
                label=user
            )

        plt.title(f"Total {score_type} over time")
        plt.ylabel(f"total {score_type}")
        plt.xlabel("time")
        plt.grid()
        if len(users) < 30:
            plt.legend()
        plt.show()