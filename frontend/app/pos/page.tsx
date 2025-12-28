'use client';

import { useState, useEffect, useRef } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '@/lib/api/client';
import { formatCurrency } from '@/lib/utils';
import { Product, SaleItem, Payment } from '@/lib/api/types';
import { ShoppingCart, Plus, Minus, Trash2, Search } from 'lucide-react';

export default function POSPage() {
  const [cart, setCart] = useState<SaleItem[]>([]);
  const [selectedShop, setSelectedShop] = useState<string>('');
  const [customer, setCustomer] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const searchInputRef = useRef<HTMLInputElement>(null);
  const queryClient = useQueryClient();

  // Auto-focus search box on mount
  useEffect(() => {
    if (searchInputRef.current) {
      searchInputRef.current.focus();
    }
  }, []);

  // Fetch products with search
  const { data: products, isLoading: productsLoading } = useQuery<Product[]>({
    queryKey: ['products', searchQuery],
    queryFn: async () => {
      const response = await apiClient.get(`/inventory/products/?search=${encodeURIComponent(searchQuery)}`);
      return response.data.results || response.data;
    },
  });

  // Filter products by search query
  const filteredProducts = products?.filter((product) =>
    product.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    product.sku?.toLowerCase().includes(searchQuery.toLowerCase())
  ) || [];

  // Fetch shops
  const { data: shops } = useQuery({
    queryKey: ['shops'],
    queryFn: async () => {
      const response = await apiClient.get('/auth/locations/?location_type=shop');
      return response.data.results || response.data;
    },
  });

  // Process sale mutation
  const saleMutation = useMutation({
    mutationFn: async (saleData: any) => {
      const response = await apiClient.post('/sales/sales/process/', saleData);
      return response.data;
    },
    onSuccess: () => {
      setCart([]);
      queryClient.invalidateQueries({ queryKey: ['sales'] });
      alert('Sale processed successfully!');
    },
  });

  const addToCart = (product: Product) => {
    const existingItem = cart.find((item) => item.product === product.id);
    
    if (existingItem) {
      setCart(
        cart.map((item) =>
          item.product === product.id
            ? { ...item, quantity: item.quantity + 1 }
            : item
        )
      );
    } else {
      setCart([
        ...cart,
        {
          id: '',
          sale: '',
          product: product.id,
          product_name: product.name,
          product_sku: product.sku,
          quantity: 1,
          unit_price: 0, // Should get from price rules
          discount_amount: 0,
          line_total: 0,
        },
      ]);
    }
  };

  const updateQuantity = (productId: string, delta: number) => {
    setCart(
      cart
        .map((item) =>
          item.product === productId
            ? { ...item, quantity: Math.max(1, item.quantity + delta) }
            : item
        )
        .filter((item) => item.quantity > 0)
    );
  };

  const removeFromCart = (productId: string) => {
    setCart(cart.filter((item) => item.product !== productId));
  };

  const calculateTotal = () => {
    return cart.reduce((sum, item) => sum + (item.unit_price * item.quantity - item.discount_amount), 0);
  };

  const handleCheckout = () => {
    if (!selectedShop) {
      alert('Please select a shop');
      return;
    }

    if (cart.length === 0) {
      alert('Cart is empty');
      return;
    }

    const saleData = {
      tenant: '', // Will be set from user context
      shop: selectedShop,
      items: cart.map((item) => ({
        product: item.product,
        quantity: item.quantity,
        unit_price: item.unit_price,
        discount_amount: item.discount_amount,
      })),
      payments: [
        {
          payment_method: 'cash',
          amount: calculateTotal(),
        },
      ],
    };

    saleMutation.mutate(saleData);
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Product Grid */}
      <div className="lg:col-span-2">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="mb-4 grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select Shop
              </label>
              <select
                value={selectedShop}
                onChange={(e) => setSelectedShop(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="">Select a shop</option>
                {shops?.map((shop: any) => (
                  <option key={shop.id} value={shop.id}>
                    {shop.name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Search Box */}
          <div className="mb-6">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                ref={searchInputRef}
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search products by name or SKU..."
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-lg"
              />
            </div>
          </div>

          <h2 className="text-xl font-semibold text-gray-900 mb-4">Products</h2>
          
          {productsLoading ? (
            <div className="animate-pulse grid grid-cols-2 md:grid-cols-3 gap-4">
              {[1, 2, 3, 4, 5, 6].map((i) => (
                <div key={i} className="bg-gray-200 h-32 rounded"></div>
              ))}
            </div>
          ) : filteredProducts.length > 0 ? (
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {filteredProducts.map((product) => (
                <button
                  key={product.id}
                  onClick={() => addToCart(product)}
                  className="bg-white border border-gray-200 rounded-lg p-4 hover:border-primary-500 hover:shadow-md transition-all text-left"
                >
                  <h3 className="font-medium text-gray-900">{product.name}</h3>
                  <p className="text-sm text-gray-500">{product.sku}</p>
                  <p className="text-lg font-semibold text-primary-600 mt-2">
                    {formatCurrency(0)} {/* Should get from price rules */}
                  </p>
                </button>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <p className="text-gray-500">No products found. Try a different search term.</p>
            </div>
          )}
        </div>
      </div>

      {/* Cart */}
      <div className="lg:col-span-1">
        <div className="bg-white rounded-lg shadow p-6 sticky top-6">
          <div className="flex items-center mb-4">
            <ShoppingCart className="h-6 w-6 text-gray-600 mr-2" />
            <h2 className="text-xl font-semibold text-gray-900">Cart</h2>
          </div>

          <div className="space-y-3 mb-4 max-h-96 overflow-y-auto">
            {cart.length === 0 ? (
              <p className="text-gray-500 text-center py-8">Cart is empty</p>
            ) : (
              cart.map((item) => (
                <div
                  key={item.product}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                >
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">{item.product_name}</p>
                    <p className="text-sm text-gray-500">
                      {formatCurrency(item.unit_price)} × {item.quantity}
                    </p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => updateQuantity(item.product, -1)}
                      className="p-1 text-gray-600 hover:text-gray-900"
                    >
                      <Minus className="h-4 w-4" />
                    </button>
                    <span className="w-8 text-center">{item.quantity}</span>
                    <button
                      onClick={() => updateQuantity(item.product, 1)}
                      className="p-1 text-gray-600 hover:text-gray-900"
                    >
                      <Plus className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => removeFromCart(item.product)}
                      className="p-1 text-red-600 hover:text-red-700 ml-2"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>

          <div className="border-t border-gray-200 pt-4">
            <div className="flex justify-between items-center mb-4">
              <span className="text-lg font-semibold text-gray-900">Total:</span>
              <span className="text-2xl font-bold text-primary-600">
                {formatCurrency(calculateTotal())}
              </span>
            </div>

            <button
              onClick={handleCheckout}
              disabled={cart.length === 0 || saleMutation.isPending}
              className="w-full bg-primary-600 text-white py-3 px-4 rounded-md font-medium hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {saleMutation.isPending ? 'Processing...' : 'Checkout'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

