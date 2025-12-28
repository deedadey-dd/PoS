"""
Validation utilities for the POS system
"""
from django.core.exceptions import ValidationError
from decimal import Decimal
from .models import Location
from inventory.models import StockBalance, Product, Batch
from sales.models import MarginRule, ShopProductCost, CreditAccount
from config.models import SystemConfiguration


class InventoryValidator:
    """
    Validators for inventory operations
    """
    
    @staticmethod
    def validate_negative_stock(location, product, quantity_out, batch=None):
        """
        Validate negative stock based on location configuration
        """
        config = SystemConfiguration.objects.filter(tenant=location.tenant).first()
        if not config:
            return True, None
        
        try:
            stock_balance = StockBalance.objects.get(
                location=location,
                product=product,
                batch=batch
            )
            available = stock_balance.available_quantity
        except StockBalance.DoesNotExist:
            available = Decimal('0')
        
        if available < quantity_out:
            behavior = location.negative_stock_behavior or config.negative_stock_behavior
            
            if behavior == 'block':
                raise ValidationError(
                    f"Insufficient stock. Available: {available}, Required: {quantity_out}"
                )
            elif behavior == 'warn':
                return False, f"Warning: Insufficient stock. Available: {available}, Required: {quantity_out}"
        
        return True, None
    
    @staticmethod
    def validate_stock_availability(location, product, quantity, batch=None):
        """
        Check if sufficient stock is available
        """
        try:
            stock_balance = StockBalance.objects.get(
                location=location,
                product=product,
                batch=batch
            )
            return stock_balance.available_quantity >= quantity, stock_balance.available_quantity
        except StockBalance.DoesNotExist:
            return False, Decimal('0')


class PricingValidator:
    """
    Validators for pricing and margin rules
    """
    
    @staticmethod
    def validate_margin(shop, product, unit_price, batch=None):
        """
        Validate margin rules for a product
        """
        # Get highest batch unit cost for this product
        if batch:
            highest_cost = batch.unit_cost
        else:
            # Get highest batch cost for this product
            batches = Batch.objects.filter(
                product=product,
                tenant=shop.tenant,
                is_active=True
            )
            if batches.exists():
                highest_cost = max(b.unit_cost for b in batches)
            else:
                # No batches, check shop cost
                shop_cost = ShopProductCost.objects.filter(
                    shop=shop,
                    product=product,
                    is_active=True
                ).first()
                if shop_cost:
                    highest_cost = shop_cost.unit_cost
                else:
                    return True, None  # No cost data, allow
        
        # Get margin rule
        margin_rule = MarginRule.objects.filter(
            tenant=shop.tenant,
            shop=shop,
            product=product,
            is_active=True
        ).first()
        
        if not margin_rule:
            # Check for shop-level rule
            margin_rule = MarginRule.objects.filter(
                tenant=shop.tenant,
                shop=shop,
                product__isnull=True,
                is_active=True
            ).first()
        
        if margin_rule:
            # Calculate margin
            if highest_cost > 0:
                margin_percent = ((unit_price - highest_cost) / highest_cost) * 100
                
                if margin_percent < margin_rule.minimum_margin_percent:
                    if margin_rule.behavior == 'block':
                        raise ValidationError(
                            f"Price violates minimum margin rule. "
                            f"Required margin: {margin_rule.minimum_margin_percent}%, "
                            f"Actual margin: {margin_percent:.2f}%"
                        )
                    elif margin_rule.behavior == 'warn':
                        return False, (
                            f"Warning: Price margin below minimum. "
                            f"Required: {margin_rule.minimum_margin_percent}%, "
                            f"Actual: {margin_percent:.2f}%"
                        )
        
        return True, None


class CreditValidator:
    """
    Validators for credit accounts
    """
    
    @staticmethod
    def validate_credit_limit(customer, amount):
        """
        Validate credit limit before sale
        """
        try:
            credit_account = customer.credit_account
        except CreditAccount.DoesNotExist:
            raise ValidationError("Customer does not have a credit account")
        
        new_balance = credit_account.current_balance + amount
        
        if new_balance > credit_account.credit_limit:
            # Check if over-limit is allowed
            if credit_account.state == 'suspended':
                raise ValidationError(
                    f"Credit account is suspended. Cannot process sale."
                )
            
            # Allow but mark as over limit
            return False, f"Credit limit exceeded. Limit: {credit_account.credit_limit}, New balance: {new_balance}"
        
        return True, None
    
    @staticmethod
    def check_credit_status(customer):
        """
        Check and update credit account status
        """
        try:
            credit_account = customer.credit_account
        except CreditAccount.DoesNotExist:
            return
        
        # Check if over limit
        if credit_account.current_balance > credit_account.credit_limit:
            if credit_account.state != 'over_limit':
                credit_account.mark_over_limit()
                credit_account.save()
        
        # Check if delinquent (based on payment terms)
        # This would require payment history analysis
        # For now, just check balance


class TransferValidator:
    """
    Validators for transfers
    """
    
    @staticmethod
    def validate_transfer_items(transfer):
        """
        Validate all items in a transfer have sufficient stock
        """
        errors = []
        for item in transfer.items.all():
            available, stock_balance = InventoryValidator.validate_stock_availability(
                transfer.from_location,
                item.product,
                item.quantity_ordered,
                item.batch
            )
            
            if not available:
                errors.append(
                    f"Insufficient stock for {item.product.name}. "
                    f"Available: {stock_balance}, Required: {item.quantity_ordered}"
                )
        
        if errors:
            raise ValidationError(errors)

