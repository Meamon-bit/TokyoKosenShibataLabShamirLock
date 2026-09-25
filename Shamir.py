import random

class Shamir:
    def __init__(self, share_num, threshold):
        self.share_num = share_num
        self.threshold = threshold
        self.modulus = 16586432895519980041857415110220152291810091712911
        # 安全のため、modulusより1桁少ない数値を扱う
        self.chunk_size = len(str(self.modulus)) - 1
        self.divisor = 10 ** self.chunk_size

    # 大きな数値を modulus より小さい数値の配列に分割
    def split_large_number(self, number):
        chunks = []
        remaining = number

        while remaining > 0:
            chunk = remaining % self.divisor
            chunks.insert(0, chunk)
            remaining //= self.divisor

        return chunks

    # 分割された数値配列を元の大きな数値に戻す
    def combine_numbers(self, number_list):
        result = 0
        for num in number_list:
            result = result * self.divisor + num
        return result

    def ramp_shares(self, chunks, ramp):
        """Generate shares for Ramp Secret Sharing."""
        secret_parts = chunks[:ramp]
        random_coeffs = [random.randint(0, self.modulus - 1) for _ in range(self.threshold - 1 - ramp)]
        coefficients = secret_parts + random_coeffs

        shares = []
        for x in range(1, self.share_num + 1):
            y = 0
            x_power = 1
            for c in coefficients:
                y = (y + c * x_power) % self.modulus
                x_power = (x_power * x) % self.modulus
            shares.append((x, y))
        return shares

    def ramp_enShamir(self, all_chunks, ramp):
        chunk_shares = []
        for i in range(0, len(all_chunks), ramp):
            chunk_group = all_chunks[i:i + ramp]
            shares = self.ramp_shares(chunk_group, ramp)
            chunk_shares.append(shares)

        combined_shares = []
        for i in range(self.share_num):
            share_parts = []
            for chunk_share in chunk_shares:
                share_parts.append(chunk_share[i])
            combined_shares.append((i + 1, share_parts))

        return combined_shares

    def create_share(self, number, ramp):
        """シェアを作成(するための前処理)"""
        if not (ramp < self.threshold <= self.share_num):
            raise ValueError("Invalid parameters: ramp must be < threshold, and threshold must be <= quantity.")
        chunks = self.split_large_number(number)
        return self.ramp_enShamir(all_chunks=chunks, ramp=ramp), len(chunks) % ramp

    def ramp_reconstruct(self, shares, n):
        """Reconstruct polynomial coefficients using Lagrange interpolation."""
        if len(shares) < self.threshold:
            raise ValueError("Insufficient shares to reconstruct the secret")
        if n >= self.threshold:
            raise ValueError("n must be less than threshold")

        shares = shares[:self.threshold]
        x_s, y_s = zip(*shares)

        def lagrange_interpolate_coefficients(x_s, y_s, degree):
            coefficients = [0] * (degree + 1)
            inv_cache = {}

            for i in range(len(x_s)):
                for j in range(len(x_s)):
                    if i != j:
                        diff = (x_s[i] - x_s[j]) % self.modulus
                        if diff not in inv_cache:
                            inv_cache[diff] = pow(diff, -1, self.modulus)

            for i in range(len(x_s)):
                xi, yi = x_s[i], y_s[i]
                basis_poly = [1]

                for j in range(len(x_s)):
                    if i != j:
                        xj = x_s[j]
                        inv = inv_cache[(xi - xj) % self.modulus]
                        new_basis = [0] * (len(basis_poly) + 1)
                        for k in range(len(basis_poly)):
                            new_basis[k] = (new_basis[k] - basis_poly[k] * xj * inv) % self.modulus
                            new_basis[k + 1] = (new_basis[k + 1] + basis_poly[k] * inv) % self.modulus
                        basis_poly = new_basis

                for k in range(len(basis_poly)):
                    if k <= degree:
                        coefficients[k] = (coefficients[k] + yi * basis_poly[k]) % self.modulus

            return coefficients[:degree + 1]

        return lagrange_interpolate_coefficients(x_s, y_s, n)

    def ramp_deShamir(self, shares, ramp, secret_length):
        num_shares_per_entry = len(shares[0][1])
        restored_share = [None] * num_shares_per_entry

        if secret_length == 0:
            for i in range(num_shares_per_entry):
                share_to_restore = [(x, s[i]) for x, s in shares]
                restored_share[i] = self.ramp_reconstruct(share_to_restore, n=ramp - 1)
        else:
            for i in range(num_shares_per_entry - 1):
                share_to_restore = [(x, s[i]) for x, s in shares]
                restored_share[i] = self.ramp_reconstruct(share_to_restore, n=ramp - 1)

            final_index = num_shares_per_entry - 1
            share_to_restore = [(x, s[final_index]) for x, s in shares]
            restored_share[final_index] = self.ramp_reconstruct(share_to_restore, n=secret_length - 1)

        flattened = [item for sublist in restored_share for item in sublist]
        return self.combine_numbers(flattened)

    def restore_number(self, shares, ramp, secret_length):
        return self.ramp_deShamir(shares, ramp, secret_length)