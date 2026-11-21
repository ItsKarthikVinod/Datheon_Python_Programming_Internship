import csv
import os

# yfinance supplies live market prices. If it is unavailable, the program can
# still load and the user receives a clear installation instruction at runtime.
try:
    import yfinance as yf
except ImportError:
    yf = None


# This dictionary acts as the in-memory portfolio, keyed by each stock ticker.
portfolio_positions = {}


def load_portfolio_from_csv(filename):
    # Loading through the CSV module lets the tracker accept portfolio files with
    # standard comma-separated headers instead of relying on fixed text parsing.
    with open(filename, "r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        required = {"Symbol", "Quantity", "Purchase Price"}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError(
                "CSV must contain Symbol, Quantity, and Purchase Price columns."
            )

        for row in reader:
            symbol = row["Symbol"].strip().upper()
            quantity = int(row["Quantity"])
            purchase_price = float(row["Purchase Price"])

            # Reject invalid portfolio values early, before they can distort totals.
            if not symbol:
                raise ValueError("Stock symbol cannot be empty.")
            if quantity <= 0:
                raise ValueError(f"Quantity for {symbol} must be greater than zero.")
            if purchase_price <= 0:
                raise ValueError(
                    f"Purchase price for {symbol} must be greater than zero."
                )

            portfolio_positions[symbol] = {
                "quantity": quantity,
                "purchase_price": purchase_price,
            }


def get_validated_integer(prompt):
    # A loop is used here so one invalid entry does not end the whole session.
    while True:
        try:
            value = int(input(prompt).strip())
            if value > 0:
                return value
            print("Value must be greater than zero.")
        except ValueError:
            print("Please enter a valid whole number.")


def get_validated_float(prompt):
    # Share prices must be positive numbers, otherwise a holding has no meaningful cost.
    while True:
        try:
            value = float(input(prompt).strip())
            if value > 0:
                return value
            print("Value must be greater than zero.")
        except ValueError:
            print("Please enter a valid number.")


def load_sp500_symbols():
    # Resolve the constituents file beside this script, so it works regardless of
    # the terminal or editor folder from which the program is launched.
    script_directory = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_directory, "constituents.csv")
    symbols = set()

    if not os.path.exists(csv_path):
        return symbols

    with open(csv_path, "r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        for row in reader:
            symbol = row.get("Symbol", "").strip().upper()
            if symbol:
                symbols.add(symbol)

    return symbols


def get_current_price(symbol):
    # A missing market-price library is reported explicitly instead of silently
    # calculating an incomplete portfolio.
    if yf is None:
        raise RuntimeError(
            "yfinance is not installed. Run: pip install yfinance"
        )

    ticker = yf.Ticker(symbol)

    try:
        # First try the most recent one-day chart, which usually contains the close price.
        history = ticker.history(period="1d")
        if history.empty:
            raise RuntimeError(f"No recent market data found for {symbol}.")
        return float(history["Close"].iloc[-1])
    except Exception:
        try:
            # fast_info is a fallback in case the normal chart response is unavailable.
            price = ticker.fast_info["last_price"]
            if price is None:
                raise RuntimeError
            return float(price)
        except Exception as error:
            raise RuntimeError(
                f"Could not retrieve the current price for {symbol}. "
                "Check the symbol and internet connection."
            ) from error


def collect_portfolio():
    # The S&P 500 list is loaded once, then used to validate every ticker the user enters.
    sp500_symbols = load_sp500_symbols()
    holding_count = get_validated_integer(
        "Enter the number of stocks to add: "
    )

    for holding_number in range(1, holding_count + 1):
        print(f"\nStock {holding_number} of {holding_count}")

        while True:
            symbol = input("Ticker symbol: ").strip().upper()
            if not symbol:
                print("Ticker symbol cannot be empty.")
            elif sp500_symbols and symbol not in sp500_symbols:
                print("Symbol is not present in the S&P 500 constituents.")
            else:
                break

        quantity = get_validated_integer("Share quantity: ")
        purchase_price = get_validated_float("Purchase price per share: ")

        # Store both the holding size and original cost; these are needed for all calculations.
        portfolio_positions[symbol] = {
            "quantity": quantity,
            "purchase_price": purchase_price,
        }


def calculate_portfolio():
    # There is nothing to calculate if the user has not entered or loaded a position.
    if not portfolio_positions:
        print("No stock positions have been added.")
        return

    total_invested = 0.0
    total_current_value = 0.0
    summary_rows = []

    print("\nPORTFOLIO PERFORMANCE")
    print(
        f"{'Ticker':<8}{'Qty':>8}{'Bought':>12}"
        f"{'Current':>12}{'Invested':>15}"
        f"{'Value':>15}{'Gain/Loss':>15}{'Change':>10}"
    )
    print("-" * 95)

    for symbol, position in portfolio_positions.items():
        quantity = position["quantity"]
        purchase_price = position["purchase_price"]

        try:
            current_price = get_current_price(symbol)
        except RuntimeError as error:
            # One unavailable ticker should not prevent the rest of the portfolio from printing.
            print(f"{symbol}: {error}")
            continue

        # Each holding is measured at two values: what it cost and what it is worth now.
        invested = purchase_price * quantity
        current_value = current_price * quantity
        gain_loss = current_value - invested
        percentage_change = (
            (gain_loss / invested) * 100 if invested else 0.0
        )

        total_invested += invested
        total_current_value += current_value

        # The formatted line gives a quick human-readable view of this one stock.
        print(
            f"{symbol:<8}{quantity:>8}"
            f"${purchase_price:>11.2f}"
            f"${current_price:>11.2f}"
            f"${invested:>14.2f}"
            f"${current_value:>14.2f}"
            f"${gain_loss:>14.2f}"
            f"{percentage_change:>9.2f}%"
        )

        summary_rows.append({
            "Symbol": symbol,
            "Quantity": quantity,
            "Purchase Price": f"{purchase_price:.2f}",
            "Current Price": f"{current_price:.2f}",
            "Invested Value": f"{invested:.2f}",
            "Current Value": f"{current_value:.2f}",
            "Gain/Loss": f"{gain_loss:.2f}",
            "Percentage Change": f"{percentage_change:.2f}",
        })

    if not summary_rows:
        print("\nNo portfolio rows could be calculated.")
        return

    # Summaries across all successful holdings show the portfolio's overall performance.
    total_gain_loss = total_current_value - total_invested
    total_percentage_change = (
        (total_gain_loss / total_invested) * 100
        if total_invested
        else 0.0
    )

    print("-" * 95)
    print(f"Total invested:       ${total_invested:,.2f}")
    print(f"Current portfolio:    ${total_current_value:,.2f}")
    print(f"Gain/loss:            ${total_gain_loss:,.2f}")
    print(f"Percentage change:    {total_percentage_change:.2f}%")

    script_directory = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_directory, "portfolio_summary.csv")
    fieldnames = [
        "Symbol",
        "Quantity",
        "Purchase Price",
        "Current Price",
        "Invested Value",
        "Current Value",
        "Gain/Loss",
        "Percentage Change",
    ]

    # Keep the transaction summary beside the script so it is easy to find and reopen.
    with open(output_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(summary_rows)

    print(f"\nSummary saved to: {output_path}")


def main():
    print("Stock Portfolio Performance Tracker")
    print("----------------------------------")
    collect_portfolio()
    calculate_portfolio()


if __name__ == "__main__":
    main()
