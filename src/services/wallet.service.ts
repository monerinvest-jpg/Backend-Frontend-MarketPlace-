export class WalletService {
    async transfer(fromUserId: number, toUserId: number, amount: number): Promise<void> {
        return await this.db.transaction(async (trx) => {
            const sender = await trx('wallets').where({ userId: fromUserId }).forUpdate().first();
            if (sender.balance < amount) throw new InsufficientFundsError();
            await trx('wallets').where({ userId: fromUserId }).decrement('balance', amount);
            await trx('wallets').where({ userId: toUserId }).increment('balance', amount);
            await trx('transactions').insert({ fromUserId, toUserId, amount, createdAt: new Date() });
        });
    }
}