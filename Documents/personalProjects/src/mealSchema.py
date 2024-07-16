import pandas as pd
import os

# Define file paths
data_folder = os.path.join(os.path.dirname(__file__), '../data')
ingredient_file_path = os.path.join(data_folder, 'food_data.csv')
recipe_file_path = os.path.join(data_folder, 'recipe_data.csv')

# Load data from CSV


def load_data(file_path, default_columns):
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    else:
        df = pd.DataFrame(columns=default_columns)
        df.to_csv(file_path, index=False)
        return df

# Save data to CSV


def save_data(df, file_path):
    df.to_csv(file_path, index=False)

# Calculate daily costs and calories


def calculate_daily_totals(df):
    df['Daily Oz'] = df['Breakfast (Oz)'] + df['Lunch (Oz)'] + \
        df['Dinner (Oz)'] + df['Snack (Oz)']
    df['Weekly Oz'] = df['Daily Oz'] * 7
    df['Weekly Cost'] = df['Weekly Oz'] * df['Cost (Oz)']
    df['Total Cost'] = df['Weekly Cost'] / 7
    df['Total Calories'] = df['Daily Oz'] * df['≈ Calories (Oz)']

    daily_cost = df['Total Cost'].sum()
    total_calories = df['Total Calories'].sum()
    breakfast_calories = (df['Breakfast (Oz)'] * df['≈ Calories (Oz)']).sum()
    lunch_calories = (df['Lunch (Oz)'] * df['≈ Calories (Oz)']).sum()
    dinner_calories = (df['Dinner (Oz)'] * df['≈ Calories (Oz)']).sum()
    snack_calories = (df['Snack (Oz)'] * df['≈ Calories (Oz)']).sum()

    return {
        'Daily Cost': daily_cost,
        'Total Calories': total_calories,
        'Breakfast Calories': breakfast_calories,
        'Lunch Calories': lunch_calories,
        'Dinner Calories': dinner_calories,
        'Snack Calories': snack_calories,
        'Calories per Cost': df['≈ Calories (Oz)'] / df['Cost (Oz)'],
        'Daily Oz': df['Daily Oz'],
        'Ingredients': df['Ingredient(s)']
    }

# Calculate recipe cost and calories


def calculate_recipe(ingredients, amounts, costs, calories):
    total_weight = sum(amounts)
    total_calories = sum(a * c for a, c in zip(amounts, calories))
    total_cost = sum(a * c for a, c in zip(amounts, costs))

    calories_per_oz = total_calories / total_weight
    cost_per_oz = total_cost / total_weight

    return {
        'Total Weight': total_weight,
        'Total Calories': total_calories,
        'Total Cost': total_cost,
        'Calories per Oz': calories_per_oz,
        'Cost per Oz': cost_per_oz
    }

# Update ingredient information


def update_ingredient(df):
    while True:
        ingredients = df['Ingredient(s)'].tolist()
        for idx, ingredient in enumerate(ingredients, start=1):
            print(f"{idx}. {ingredient}")

        choice = int(input(
            "Enter the number corresponding to the ingredient you want to modify (or 0 to go back): ")) - 1
        if choice == -1:
            return df  # Go back to the previous menu
        if 0 <= choice < len(ingredients):
            ingredient = ingredients[choice]
            while True:
                print("What do you want to update?")
                print("1. Cost (Oz)")
                print("2. ≈ Calories (Oz)")
                print("3. Breakfast (Oz)")
                print("4. Lunch (Oz)")
                print("5. Dinner (Oz)")
                print("6. Snack (Oz)")
                print("7. Calculate and Store Recipe")
                print("8. Go back")
                column_choice = input("Enter your choice (1-8): ")

                if column_choice == '7':
                    store_recipe(df)
                    break
                elif column_choice == '8':
                    break
                else:
                    column_map = {
                        '1': 'Cost (Oz)',
                        '2': '≈ Calories (Oz)',
                        '3': 'Breakfast (Oz)',
                        '4': 'Lunch (Oz)',
                        '5': 'Dinner (Oz)',
                        '6': 'Snack (Oz)'
                    }
                    column = column_map.get(column_choice)
                    if column:
                        value = float(
                            input(f"Enter the new value for {column}: "))
                        df.loc[df['Ingredient(s)'] ==
                               ingredient, column] = value
                        print(f"{ingredient} updated successfully.")
                    else:
                        print("Invalid choice.")
        else:
            print("Invalid number.")
    return df

# Add a new ingredient


def add_ingredient(df):
    while True:
        ingredient = input(
            "Enter the new ingredient name (or type 'back' to go back): ")
        if ingredient.lower() == 'back':
            return df
        cost_oz = float(input("Enter the cost per oz: "))
        calories_oz = float(input("Enter the calories per oz: "))
        breakfast_oz = float(input("Enter the breakfast amount in oz: "))
        lunch_oz = float(input("Enter the lunch amount in oz: "))
        dinner_oz = float(input("Enter the dinner amount in oz: "))
        snack_oz = float(input("Enter the snack amount in oz: "))

        new_row = pd.DataFrame({
            'Ingredient(s)': [ingredient],
            'Cost (Oz)': [cost_oz],
            '≈ Calories (Oz)': [calories_oz],
            'Breakfast (Oz)': [breakfast_oz],
            'Lunch (Oz)': [lunch_oz],
            'Dinner (Oz)': [dinner_oz],
            'Snack (Oz)': [snack_oz]
        })

        df = pd.concat([df, new_row], ignore_index=True)
        print(f"{ingredient} added successfully.")
        return df

# Store recipe data and update master food list


def store_recipe(master_df):
    print("Enter details for the recipe:")
    ingredients = []
    amounts = []
    costs = []
    calories = []

    while True:
        ingredient = input("Enter ingredient name (or 'done' to finish): ")
        if ingredient.lower() == 'done':
            break
        amount = float(input(f"Enter amount of {ingredient} in oz: "))
        cost = float(input(f"Enter cost per oz of {ingredient}: "))
        cal = float(input(f"Enter calories per oz of {ingredient}: "))

        ingredients.append(ingredient)
        amounts.append(amount)
        costs.append(cost)
        calories.append(cal)

    recipe_totals = calculate_recipe(ingredients, amounts, costs, calories)

    # Store in recipe_data.csv
    recipe_df = load_data(recipe_file_path, ['Ingredient(s)', 'Amount (Oz)', 'Cost (Oz)', '≈ Calories (Oz)',
                          'Total Weight (Oz)', 'Total Calories', 'Total Cost', 'Calories per Oz', 'Cost per Oz'])
    new_recipe = pd.DataFrame({
        'Ingredient(s)': [", ".join(ingredients)],
        'Amount (Oz)': [", ".join(map(str, amounts))],
        'Cost (Oz)': [", ".join(map(str, costs))],
        '≈ Calories (Oz)': [", ".join(map(str, calories))],
        'Total Weight (Oz)': [recipe_totals['Total Weight']],
        'Total Calories': [recipe_totals['Total Calories']],
        'Total Cost': [recipe_totals['Total Cost']],
        'Calories per Oz': [recipe_totals['Calories per Oz']],
        'Cost per Oz': [recipe_totals['Cost per Oz']]
    })
    recipe_df = pd.concat([recipe_df, new_recipe], ignore_index=True)
    save_data(recipe_df, recipe_file_path)
    print(f"Recipe stored successfully.")

    # Add to master food list
    master_df = add_recipe_to_master(master_df, ingredients, recipe_totals)
    return master_df

# Add recipe to master food list


def add_recipe_to_master(master_df, ingredients, recipe_totals):
    recipe_name = "Recipe: " + ", ".join(ingredients)
    new_row = pd.DataFrame({
        'Ingredient(s)': [recipe_name],
        'Cost (Oz)': [recipe_totals['Cost per Oz']],
        '≈ Calories (Oz)': [recipe_totals['Calories per Oz']],
        'Breakfast (Oz)': [0],
        'Lunch (Oz)': [0],
        'Dinner (Oz)': [0],
        'Snack (Oz)': [0]
    })
    master_df = pd.concat([master_df, new_row], ignore_index=True)
    print(f"{recipe_name} added to the master food list.")
    return master_df

# Display complete breakdown


def display_breakdown(totals):
    monthly_cost = totals['Daily Cost'] * 30
    print(f"Daily Cost: ${totals['Daily Cost']:.2f}")
    print(f"Monthly Cost: ${monthly_cost:.2f}")
    print(f"Total Calories: {totals['Total Calories']:.2f}")
    print(f"Breakfast Calories: {totals['Breakfast Calories']:.2f}")
    print(f"Lunch Calories: {totals['Lunch Calories']:.2f}")
    print(f"Dinner Calories: {totals['Dinner Calories']:.2f}")
    print(f"Snack Calories: {totals['Snack Calories']:.2f}")

    # Show the calories per cost ratio for each ingredient
    ratio_df = pd.DataFrame({
        'Ingredient': totals['Ingredients'],
        'Calories per Cost': totals['Calories per Cost'],
        'Daily Oz': totals['Daily Oz']
    }).sort_values(by='Calories per Cost', ascending=False)

    ratio_df['Details'] = ratio_df.apply(
        lambda x: f"{x['Calories per Cost']:.2f} ({x['Daily Oz']:.2f} oz/day)", axis=1)
    ratio_df = ratio_df[['Ingredient', 'Details']]

    print("\nCalories per Cost Ratio (ranked from best to worst):")
    print(ratio_df.to_string(index=False))

# Main function to run the program


def main(file_path):
    df = load_data(file_path, ['Ingredient(s)', 'Cost (Oz)', '≈ Calories (Oz)',
                   'Breakfast (Oz)', 'Lunch (Oz)', 'Dinner (Oz)', 'Snack (Oz)'])

    while True:
        print("\nHello, where do you want to start:")
        print("1. See complete breakdown")
        print("2. Modify ingredient")
        print("3. Add new ingredient")
        print("4. Exit")
        choice = input("Enter your choice (1-4): ")

        if choice == '1':
            totals = calculate_daily_totals(df)
            display_breakdown(totals)
        elif choice == '2':
            df = update_ingredient(df)
            save_data(df, file_path)
        elif choice == '3':
            df = add_ingredient(df)
            save_data(df, file_path)
        elif choice == '4':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main(ingredient_file_path)
